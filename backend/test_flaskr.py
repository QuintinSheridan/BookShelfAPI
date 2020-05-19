import unittest
import os
from flaskr import create_app
from models import setup_db, Book

class BookshelfTestCase(unittest.TestCase):
    """This class represents the Bookshelf API test case"""

    def setUp(self):
        """Executed before each test. Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        user = os.environ['USERNAME']
        pword = os.environ['PW']
        db_name = 'bookshelf_test'

        self.database_path = f'postgres://{user}:{pword}@localhost:5432/{db_name}'
        setup_db(self.app, self.database_path)

        self.new_book = {
            'title': 'Yo Yo Ma',
            'author': 'Dr. Dude',
            'rating': '5'
        }

        self.delete_id = 0

        pass

    def tearDown(self):
        """Executed after each test"""
        pass
        
    def test_get_books(self):
        """test homepage get books request"""
        response = self.client().get('/books')
        body = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertTrue(body['total_books'])
        self.assertTrue(len(body['books']))

    def test_404_get_bad_page(self):
        # request a book id that doesn't exist
        response = self.client().get('/books?page=1000')
        body = response.get_json()

        self.assertEqual(body['success'], False)
        self.assertEqual(body['error'], 404)


    def test_update_book_rating(self):
        response = self.client().patch('books/1', json={'rating':1})
        body  = response.get_json()
        book = Book.query.filter(Book.id == 1).one_or_none()

        self.assertEqual(body['id'],1)
        self.assertEqual(body['success'], True)
        self.assertEqual(book.format()['rating'], 1)

    def test_400_for_failed_update(self):
        response = self.client().patch('/books/5')
        data = response.get_json()

        self.assertEqual(data['error'], 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')




    # def test_404_update_bad_book_rating(self):
    #     response = self.client().patch('books/1000', json={'rating':1})
    #     body=response.get_json()

    #     self.assertEqual(body['success'], False)
    #     self.assertEqual(response.status_code, 400)


    def test_create_book(self):
        new_book = self.new_book
        response = self.client().post('books', json={'title':new_book['title'], 'author':new_book['author'], 'rating':new_book['rating']})
        body = response.get_json()

        self.assertTrue(body['total_books'])
        self.assertTrue(body['books'])
        self.assertEqual(body['success'], True)
        self.assertTrue(body['created'])

        # set id of created book for testing deletion
        self.delete_id = body['created']


    # def test_delete_existing_book(self):
    #     print(f'self.delete_id {self.delete_id}')
    #     endpoint = f'/books/{self.delete_id}'
    #     response = self.client().delete(endpoint)
    #     body = response.get_json()

    #     self.assertEqual(body['success'], True)
    #     self.assertEqual(body['deleted'], book_id)
    #     self.assertTrue(body['books'])

if __name__=='__main__':
    unittest.main()




