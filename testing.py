try:
    from app import app
    import unittest


except Exception as e:
    print("some modules are missing {}".format(e))


class Test(unittest.TestCase):
    # check if responses is 200
    def test_user_register(self):
        test = app.test_client(self)
        response = test.get('/user-registration/')
        status = response.status_code
        self.assertEqual(status, 405)

    def test_products(self):
        test = app.test_client(self)
        response = test.get('/get-products/')
        status = response.status_code
        self.assertEqual(status, 200)

    def test_product_id(self):
        test = app.test_client(self)
        response = test.get('/get-product/3/')
        status = response.status_code
        self.assertEqual(status, 200)

    # check content type
    def test_type(self):
        test = app.test_client(self)
        response = test.get('/get-products/')
        self.assertEqual(response.content_type, "application/json")


if __name__ == '__main__':
    unittest.main()
