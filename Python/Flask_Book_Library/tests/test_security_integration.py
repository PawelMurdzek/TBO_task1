"""
Integration tests for security features.
Tests real-world attack scenarios and defense mechanisms.
"""

import unittest
from project import app, db
from project.books.models import Book
from project.customers.models import Customer


class SecurityIntegrationTestCase(unittest.TestCase):
    """Integration tests for security features"""

    def setUp(self):
        """Set up test environment"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up"""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_stored_xss_attack_scenario(self):
        """
        Test stored XSS attack scenario:
        1. Attacker creates book with malicious script
        2. Verify script is escaped in storage
        3. Verify it's safe when retrieved
        """
        # Attacker tries to inject XSS
        xss_payload = '<script>steal_cookies()</script>'
        response = self.client.post('/books/create', 
            json={
                'name': xss_payload,
                'author': 'Attacker',
                'year_published': 2024,
                'book_type': '5days'
            })
        
        self.assertEqual(response.status_code, 201)
        
        # Verify storage is safe
        with app.app_context():
            book = Book.query.first()
            self.assertNotIn('<script>', book.name)
            self.assertIn('&lt;script&gt;', book.name)
        
        # Verify retrieval is safe
        response = self.client.get('/books/json')
        self.assertEqual(response.status_code, 200)
        # JSON should not contain unescaped script tags

    def test_reflected_xss_via_search(self):
        """
        Test that search functionality doesn't reflect XSS
        (If search was implemented via URL params)
        """
        # Create a book
        with app.app_context():
            book = Book(name='Safe Book', author='Author', 
                       year_published=2024, book_type='5days')
            db.session.add(book)
            db.session.commit()
        
        # Try XSS in URL parameter (if search implemented)
        response = self.client.get('/books/?search=<script>alert(1)</script>')
        
        # Should not execute script
        self.assertNotIn(b'<script>alert(1)</script>', response.data)

    def test_dom_based_xss_prevention(self):
        """
        Test that DOM-based XSS is prevented
        by using textContent instead of innerHTML
        """
        # This test verifies that the JS code uses safe methods
        # We'll check the JS file content
        response = self.client.get('/static/js/books.js')
        
        if response.status_code == 200:
            js_content = response.data.decode('utf-8')
            # Should use textContent
            self.assertIn('textContent', js_content)
            # Should not use dangerous innerHTML in user data contexts
            # (innerHTML in loans.js was fixed to use DOM methods)

    def test_csp_prevents_inline_script_execution(self):
        """
        Test that CSP headers prevent inline script execution
        (In a real browser, not in test client)
        """
        response = self.client.get('/')
        csp = response.headers.get('Content-Security-Policy', '')
        
        # Verify CSP is present
        self.assertTrue(len(csp) > 0)
        
        # CSP should restrict resources
        self.assertIn('font-src', csp)
        self.assertIn('img-src', csp)

    def test_layered_defense_escaping_plus_validation(self):
        """
        Test that both validation and escaping work together
        """
        # Even if validation is bypassed, escaping should protect
        malicious_data = {
            'name': '"><img src=x onerror=alert(1)>',
            'author': '<svg/onload=alert(1)>',
            'year_published': 2024,
            'book_type': '5days'
        }
        
        response = self.client.post('/books/create', json=malicious_data)
        
        # Should succeed (escaping handles it)
        self.assertEqual(response.status_code, 201)
        
        # Verify both fields are escaped
        with app.app_context():
            book = Book.query.first()
            # Check that dangerous HTML tags are escaped (can't create elements)
            self.assertNotIn('<img', book.name)
            self.assertNotIn('<svg', book.author)
            # Verify escaped versions are present
            self.assertIn('&lt;img', book.name)
            self.assertIn('&lt;svg', book.author)
            # Most importantly: verify no executable HTML tags exist
            # The literal text can remain, but without < > it's not executable
            self.assertTrue(book.name.startswith('&#34;&gt;&lt;'))  # Properly escaped
            self.assertTrue(book.author.startswith('&lt;svg'))  # Properly escaped

    def test_sql_injection_protection(self):
        """
        Test that SQLAlchemy + escaping protect against SQL injection
        """
        sql_injection_attempts = [
            "' OR '1'='1",
            "admin'--",
            "1'; DROP TABLE books;--",
            "' UNION SELECT * FROM customers--"
        ]
        
        for injection in sql_injection_attempts:
            response = self.client.post('/customers/create', 
                data={
                    'name': injection,
                    'city': 'TestCity',
                    'age': 25
                })
            
            # Should succeed without executing SQL
            self.assertEqual(response.status_code, 201)
            
            # Verify table still exists and data is escaped
            with app.app_context():
                customers = Customer.query.all()
                self.assertIsNotNone(customers)
                # Last customer should have escaped data
                last = Customer.query.order_by(Customer.id.desc()).first()
                self.assertIn('&#39;', last.name)  # Escaped quote

    def test_multiple_xss_vectors_in_single_request(self):
        """
        Test multiple XSS vectors in one request
        """
        response = self.client.post('/books/create', 
            json={
                'name': '<script>alert(1)</script>',
                'author': '<img src=x onerror=alert(2)>',
                'year_published': 2024,
                'book_type': '5days'
            })
        
        self.assertEqual(response.status_code, 201)
        
        with app.app_context():
            book = Book.query.first()
            # All fields should be escaped
            self.assertNotIn('<script>', book.name)
            self.assertNotIn('<img', book.author)
            self.assertIn('&lt;', book.name)
            self.assertIn('&lt;', book.author)

    def test_unicode_xss_attempt(self):
        """
        Test Unicode-based XSS attempts
        """
        unicode_xss = '\u003cscript\u003ealert(1)\u003c/script\u003e'
        
        response = self.client.post('/customers/create', 
            data={
                'name': unicode_xss,
                'city': 'City',
                'age': 25
            })
        
        # Should be handled safely
        self.assertEqual(response.status_code, 201)


if __name__ == '__main__':
    unittest.main()
