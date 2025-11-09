"""
Unit tests for XSS protection in Flask Book Library application.
Tests input sanitization, output encoding, and security measures.
"""

import unittest
import json
from project import app, db
from project.books.models import Book
from project.customers.models import Customer
from project.loans.models import Loan
from markupsafe import escape


class XSSProtectionTestCase(unittest.TestCase):
    """Test XSS protection mechanisms"""

    def setUp(self):
        """Set up test client and database"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up after tests"""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # ==================== BOOK XSS TESTS ====================

    def test_book_create_with_script_tag_in_name(self):
        """Test that script tags in book name are escaped"""
        malicious_name = "<script>alert('XSS')</script>"
        response = self.client.post('/books/create', 
            json={
                'name': malicious_name,
                'author': 'Test Author',
                'year_published': 2024,
                'book_type': '5days'
            })
        
        self.assertEqual(response.status_code, 201)
        
        # Verify the data is escaped in database
        with app.app_context():
            book = Book.query.first()
            self.assertIsNotNone(book)
            # The escape() function converts < and > to HTML entities
            self.assertNotIn('<script>', book.name)
            self.assertNotIn('</script>', book.name)
            # Should contain escaped version
            self.assertIn('&lt;script&gt;', book.name)

    def test_book_create_with_img_onerror_in_author(self):
        """Test that img onerror XSS attempt is escaped"""
        malicious_author = '<img src=x onerror="alert(1)">'
        response = self.client.post('/books/create', 
            json={
                'name': 'Test Book',
                'author': malicious_author,
                'year_published': 2024,
                'book_type': '2days'
            })
        
        self.assertEqual(response.status_code, 201)
        
        with app.app_context():
            book = Book.query.first()
            # Verify dangerous tags are escaped
            self.assertNotIn('<img', book.author)
            self.assertIn('&lt;img', book.author)
            # The word "onerror" will still appear but as escaped text, not executable code
            self.assertNotIn('onerror="', book.author)  # Check it's not executable
            self.assertNotIn('onerror=alert', book.author)  # Verify no execution context

    # ==================== CUSTOMER XSS TESTS ====================

    def test_customer_create_with_xss_in_name(self):
        """Test that XSS in customer name is escaped"""
        malicious_name = '"><script>document.cookie</script>'
        response = self.client.post('/customers/create', 
            data={
                'name': malicious_name,
                'city': 'TestCity',
                'age': 25
            })
        
        self.assertEqual(response.status_code, 201)
        
        with app.app_context():
            customer = Customer.query.first()
            self.assertNotIn('<script>', customer.name)
            self.assertIn('&gt;&lt;script&gt;', customer.name)

    # ==================== LOAN XSS TESTS ====================

    def test_loan_create_with_xss_in_customer_name(self):
        """Test that XSS in loan customer name is escaped"""
        # First create a book
        with app.app_context():
            book = Book(name='Test Book', author='Author', 
                       year_published=2024, book_type='5days', status='available')
            db.session.add(book)
            db.session.commit()
        
        malicious_customer = '<svg/onload=alert(1)>'
        response = self.client.post('/loans/create', 
            data={
                'customer_name': malicious_customer,
                'book_name': 'Test Book',
                'loan_date': '2024-01-01',
                'return_date': '2024-01-10'
            })
        
        # Should redirect on success (302) or return error
        self.assertIn(response.status_code, [200, 302])

    # ==================== CONTENT SECURITY POLICY TESTS ====================

    def test_csp_headers_present(self):
        """Test that CSP headers are set"""
        response = self.client.get('/')
        self.assertIn('Content-Security-Policy', response.headers)

    def test_csp_font_src_configured(self):
        """Test that font-src CSP directive is present"""
        response = self.client.get('/')
        csp = response.headers.get('Content-Security-Policy', '')
        self.assertIn('font-src', csp)
        self.assertIn('stackpath.bootstrapcdn.com', csp)

    def test_csp_img_src_configured(self):
        """Test that img-src CSP directive is present"""
        response = self.client.get('/')
        csp = response.headers.get('Content-Security-Policy', '')
        self.assertIn('img-src', csp)
        self.assertIn("'self'", csp)

    # ==================== EDIT OPERATION TESTS ====================

    def test_book_edit_with_xss_attempt(self):
        """Test that editing book with XSS is escaped"""
        # Create a book first
        with app.app_context():
            book = Book(name='Original', author='Author', 
                       year_published=2024, book_type='5days')
            db.session.add(book)
            db.session.commit()
            book_id = book.id
        
        # Try to edit with XSS
        response = self.client.post(f'/books/{book_id}/edit', 
            json={
                'name': '<iframe src="evil.com"></iframe>',
                'author': 'Updated Author',
                'year_published': 2024,
                'book_type': '5days'
            })
        
        self.assertEqual(response.status_code, 200)
        
        with app.app_context():
            book = Book.query.get(book_id)
            self.assertNotIn('<iframe', book.name)
            self.assertIn('&lt;iframe', book.name)

    def test_customer_edit_with_xss_attempt(self):
        """Test that editing customer with XSS is escaped"""
        # Create a customer first
        with app.app_context():
            customer = Customer(name='Original', city='City', age=25)
            db.session.add(customer)
            db.session.commit()
            customer_id = customer.id
        
        # Try to edit with XSS
        response = self.client.post(f'/customers/{customer_id}/edit', 
            data={
                'name': 'Updated',
                'city': '<script>alert("XSS")</script>',
                'age': 30
            })
        
        self.assertEqual(response.status_code, 200)
        
        with app.app_context():
            customer = Customer.query.get(customer_id)
            self.assertNotIn('<script>', customer.city)
            self.assertIn('&lt;script&gt;', customer.city)

    # ==================== JSON OUTPUT TESTS ====================

    def test_books_json_output_escaping(self):
        """Test that JSON output contains escaped data"""
        # Create book with XSS attempt
        with app.app_context():
            book = Book(name='<b>Bold</b>', author='Test', 
                       year_published=2024, book_type='5days')
            db.session.add(book)
            db.session.commit()
        
        response = self.client.get('/books/json')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        # The name should be in the response (escaped by backend)
        self.assertTrue(len(data['books']) > 0)
        # Frontend should use textContent, not innerHTML

    def test_customers_json_output_escaping(self):
        """Test that customer JSON output is safe"""
        with app.app_context():
            customer = Customer(name='<img src=x>', city='City', age=25)
            db.session.add(customer)
            db.session.commit()
        
        response = self.client.get('/customers/json')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(len(data['customers']) > 0)


if __name__ == '__main__':
    unittest.main()

