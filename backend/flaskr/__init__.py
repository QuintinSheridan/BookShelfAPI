import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy #, or_
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there. 
#     If you do not update the endpoints, the lab will not work - of no fault of your API code! 
#   - Make sure for each route that you're thinking through when to abort and with which kind of error 
#   - If you change any of the response body keys, make sure you update the frontend to correspond. 

def paginate_books(request,selection):
  page = request.args.get('page', 1, type=int)
  start = (page-1)*BOOKS_PER_SHELF
  end = start+BOOKS_PER_SHELF

  books = [book.format() for book in selection]
  current_books = books[start:end]

  return current_books


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)


  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  # @TODO: Write a route that retrivies all books, paginated. 
  #         You can use the constant above to paginate by eight books.
  #         If you decide to change the number of books per page,
  #         update the frontend to handle additional books in the styling and pagination
  #         Response body keys: 'success', 'books' and 'total_books'
  # TEST: When completed, the webpage will display books including title, author, and rating shown as stars

  ##################
  # App Api Routes #
  ##################

  @app.route('/books', methods=['GET'])
  def get_books():
    books = Book.query.order_by(Book.id).all()
    total_books = len(books)
    current_books = paginate_books(request,books)
   
    if len(current_books) == 0:
      abort(404)
    else:
      response = jsonify({
        'books':current_books,
        'total_books':total_books,
        'success':True
      })

    return response

  

  # @TODO: Write a route that will update a single book's rating. 
  #         It should only be able to update the rating, not the entire representation
  #         and should follow API design principles regarding method and route.  
  #         Response body keys: 'success'
  # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh
  @app.route('/books/<int:book_id>', methods=['PATCH'])
  def update_rating(book_id):
    try:
      body = request.get_json()
      print(f'\n\n\n body: {body} \n\n\n')
      book = Book.query.filter(Book.id == book_id).one_or_none()
      if book is None:
        abort(404)
      
      if 'rating' in body:
        book.rating = int(body['rating'])
        book.update()
        
        return jsonify({'success':True, 'id':book.id})

    except:
      abort(400)



  # @TODO: Write a route that will delete a single book. 
  #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
  #        Response body keys: 'success', 'books' and 'total_books'
  @app.route('/books/<int:book_id>', methods=['DELETE'])
  def delete_book(book_id):
    book = Book.query.get(book_id)
    if book is None:
      abort(404)
    else:
      book.delete()
    
    books = Book.query.all()
    current_books = paginate_books(request, books)

    return jsonify({
      'success': True,
      'books': current_books,
      'total_books': len(books), 
      'deleted': book.id
    })


  # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.

  @app.route('/books', methods=['POST'])
  def create_book():
    try:
      body = request.get_json()
      print(f'\n\n\n body: {body} \n\n\n')
      new_title = body.get('title', None)
      new_author = body.get('author', None)
      new_rating = int(body.get('rating', None))

      book = Book(title=new_title, author=new_author, rating=new_rating)
      print('book instantiated')
      book.insert()
      print('book inserted')
      books = Book.query.order_by(Book.id).all()
      current_books = paginate_books(request, books)

      print('WTF')
      return jsonify({
        'success': True,
        'created': book.id,
        'books': current_books,
        'total_books': len(books)
      })

    except:
      abort(422)


  ##################
  # Error Handling #
  ##################

  @app.errorhandler(404)
  def resource_not_found(error):
    return jsonify({
      'success': False,
      "error": 404,
      "message": 'resource not found'
    })

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      "error": 400,
      "message": 'bad request'
    })

  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      'success': False,
      "error": 422,
      "message": 'unprocessable entity'
    })

  @app.errorhandler(405)
  def invalid_method(error):
    return jsonify({
      'success': False,
      "error": 405,
      "message": 'invalid method'
    })


  return app


  