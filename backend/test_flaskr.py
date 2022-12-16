import json
import os
import unittest

from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import Category, Question, setup_db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
                        "student", "student", "localhost:5432", self.database_name
                       )

        setup_db(self.app, self.database_path)
        self.newQuestion={"question": "which is the Lebron James nationality?",
                         "answer": "american", "category": 6, "difficulty": 1}
        
        self.newQuestion3={"question":"which is the first president of america",
                          "answer":"Georges Washington","category":4, "difficulty":3}
        self.quiz_sample={"previous_questions":[],"quiz_category": {"type":"Science", "id":1}}
        self.fail_sample={"previous_questions":[],"quiz_category": {"type":"Fashion", "id":8}}
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_all_the_categories(self):
        res=self.client().get("/categories")
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_categories"])

    def test_categories_error(self):
        res=self.client().get("/categories/8")
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"],"resource not found")


    def test_get_paginated_questions(self):
        res=self.client().get("/questions")
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_requesting_invalid_page(self):
        res= self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data['questions'], [])
        self.assertEqual(len(data["questions"]),0)

    def test_get_questions_search_with_results(self):
        res= self.client().post("/questions/searchTerm", json={"searchTerm": "what"})
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
    
    def test_get_questions_search_without_results(self):
        res=self.client().post("/questions/searchTerm", json={"searchTerm":"katana"})
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)  
        self.assertEqual(len(data["questions"]),0)

    def test_delete_questions(self):
        res=self.client().delete("/questions/10")
        data=json.loads(res.data)
        
        questions=Question.query.filter(Question.id==10).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"],10)
        self.assertTrue(data["TotalQuestions"])
        self.assertEqual(questions,None)


    def test_422_if_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_creating_of_question(self):
        res=self.client().post("/questions", json=self.newQuestion)
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True) 
        self.assertTrue(["created"]) 
        self.assertTrue(len(data["questions"]))

    def test_creating_error_of_question(self):
        res=self.client().post("/questions/17", json=self.newQuestion3)
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    def test_categories_id_of_questions_with_success(self):
        res=self.client().get("/categories/1/questions")
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]),3)

    def test_categories_id_of_questions_without_success(self):
        res=self.client().get("/categories/8/questions" )
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]),0)
        
    def test_quizzes_with_success(self):
        res=self.client().post("/quizzes", json=self.quiz_sample)
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        
    def test_quizzes_without_success(self):
        res=self.client().post("/quizzes", json=self.fail_sample)
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
       
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()