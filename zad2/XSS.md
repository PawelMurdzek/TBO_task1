# XSS
## 1. Znalezienie podatności:

### Podatność:
Po wpisaniu w dowolne miejsce z dodaniem recordu następującej linijki: 
```
<img src=x onerror=alert('123124!')>
```
Pozwala na wyświetlanie tego alertu po wykonaniu każdej operacji na zakładce, w której to zrobiliśmy. 
Takimi operacjami może być odświeżenie, dodanie nowego rekordu. Po wejściu na tą stronę z innej przeglądarki, nasz kod XSS dalej działa tak samo - udało się nam wstrzyknąć kod !!!

### Rozwalenie strony
Po spróbowaniu dodania opcji "Add New Loan" z podatnymi wartościami po prostu pada.

``` javascript
{"error":"Error creating loan: (sqlite3.IntegrityError) NOT NULL constraint failed: Loans.loan_date\n[SQL: INSERT INTO \"Loans\" (customer_name, book_name, loan_date, return_date, original_author, original_year_published, original_book_type) VALUES (?, ?, ?, ?, ?, ?, ?)]\n[parameters: (\"<img src=x onerror=alert('123124!')>\", \"<img src=x onerror=alert('XSS!')>\", None, '0011-11-11 00:00:00.000000', \"<img src=x onerror=alert('XSS!')>\", 1, '2days')]\n(Background on this error at: https://sqlalche.me/e/20/gkpj)"}
```

## 2. Zaproponowanie poprawki:

* Usunięcie kewordów `|safe`z pól inputów w rekordach
* Dodanie biblioteki `from markupsafe import escape`, aby walidować inputy, dzięki temu `<img src=x onerror=alert('123124!')>` staje się `&lt;img src=x onerror=alert(&#39;111&#39;)&gt;`
* Dodatkowo dodałem reguły regexowe do kontruktorów do książek i ludzi
* Użycie kontruktorów `CreateCustomer()` oraz `CreateBook()`, zamiast ślepych query_all()
* `textContent` zamiast `innerHTML` jako bezpieczniejszy DOM w loans.js
* Dodanie headerów CSP w __init.py___:
** Atakujący nie może wstrzyknąć kodu który załaduje złośliwe czcionki z evil.com
** Nie można załadować obrazów ze zdalnych serwerów (chroni przed tracking pixels, phishing images)

## 3. Testy jednostkowe

* Dodanie w testów do XSS, sprawdzam tam wstrzyknięcie takich wartości jak `<script>alert("XSS")</script>`.