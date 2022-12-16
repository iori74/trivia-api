import os
from calendar import c
from collections.abc import Mapping
from operator import truediv
from random import randrange, choice

from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import Category, Question, db, setup_db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization, true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, PATCH,POST,DELETE,OPTIONS')
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    all_category = Category.query.order_by(Category.id).all()
    category_displaying = {
        category.id: category.type for category in all_category}

    @app.route('/categories')
    def category_handle():

        return jsonify(
            {
                'categories': category_displaying,
                'success': True,
                'total_categories': len(Category.query.all())
            }
        )

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    def pagination_request(question):
        page = request.args.get("page", 1, type=int)
        begin = (page - 1) * QUESTIONS_PER_PAGE
        end = begin + QUESTIONS_PER_PAGE
        question_filter = [questionlist.format() for questionlist in question]
        question_filter1 = question_filter[begin:end]
        return question_filter1

    @app.route('/questions', methods=['GET'])
    def questions_handle():
        all_the_question = Question.query.order_by(Question.id).all()
        list_of_question = pagination_request(all_the_question)

        if list_of_question == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': list_of_question,
            'total_questions': len(Question.query.all()),
            'categories': category_displaying
        })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def questions_removal(id):

        try:
            questions = Question.query.filter(Question.id == id).one_or_none()

            if questions is None:
                abort(404)

            questions.delete()

            return jsonify(
                {
                    'success': True,
                    'deleted': id,
                    'TotalQuestions': len(Question.query.all())
                }
            )
        except BaseException:
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def question_creating():
        data_request = request.get_json()
        new_question = data_request.get('question', None)
        new_answer = data_request.get('answer', None)
        new_category = data_request.get('category', None)
        new_difficulty = data_request.get('difficulty', None)

        try:
            new_questions = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty)
            new_questions.insert()

            all_the_questions = Question.query.order_by(Question.id).all()
            current_questions = pagination_request(all_the_questions)

            return jsonify({
                'success': True,
                'created': new_questions.id,
                'questions': current_questions,
                'TotalQuestions': len(Question.query.all())
            })
        except BaseException:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/searchTerm', methods=['POST'])
    def search_term():
        data_request = request.get_json()
        searchTerm = data_request.get('searchTerm', None)
        all_the_questions = Question.query.order_by(Question.id).all()
        current_questions = pagination_request(all_the_questions)

        if searchTerm:
            questions = Question.query.order_by(
                Question.id).filter(
                Question.question.ilike(
                    '%{}%'.format(searchTerm)))
            searchQuestion = pagination_request(questions)
            return jsonify({
                'success': True,
                'questions': searchQuestion,
                'totalQuestions': len(Question.query.all()),
            })
        elif searchTerm == '':
            return jsonify({
                'success': True,
                'questions': current_questions,
                'totalQuestions': len(Question.query.all())
            })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def only_questions(id):
        questions_getting = db.session.query(Question).join(
            Category, Category.id == Question.category).filter(
            Question.category == id)
        real_questions = pagination_request(questions_getting)
        return jsonify({
            'success': True,
            'questions': real_questions,
            'totalQuestions': len(Question.query.all())
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def quizzes_creating():
        data_request = request.get_json()
        quiz_category = data_request.get('quiz_category', None)
        previous_questions = data_request.get('previous_questions', None)

        if quiz_category == {'type': 'click', 'id': 0}:
            print(quiz_category)
            all_the_questions = Question.query.all()
            random_quest = [
                questionlist.id for questionlist in all_the_questions]
            try:
                quiz = choice(
                    [questionlist for questionlist in random_quest if questionlist not in previous_questions])
            except BaseException:
                quiz = None
            if quiz is None:
                return jsonify({
                    'question': {}

                })
            quiz2 = Question.query.filter(Question.id == quiz).one_or_none()
            if quiz2 is None:
                return jsonify({'success': False, 'question': {}})
            return ({
                'success': True,
                'question': quiz2.format()
            })

        else:
            category_join = Question.query.filter_by(
                category=quiz_category['id']).filter(
                Question.id.notin_(
                    (previous_questions))).all()

            specific_questions = category_join[randrange(
                0, len(category_join))].format() if len(category_join) > 0 else None

            return jsonify(
                {'question': specific_questions, 'success': True, })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def notFound(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(405)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'internal server error'
        }), 500

    return app
