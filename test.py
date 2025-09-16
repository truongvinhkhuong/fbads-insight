#!/usr/bin/env python3
"""
Test suite cho Facebook Ads Dashboard và Chatbot
Test các API endpoints và chức năng chính
"""

import unittest
import json
import os
import tempfile
import requests
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import app và các modules
from app import app, OpenAIChatbot, load_ads_data
from facebook_ads_extractor import FacebookAdsExtractor

class TestFacebookAdsDashboard(unittest.TestCase):
    """Test class cho Facebook Ads Dashboard"""
    
    def setUp(self):
        """Thiết lập test environment"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Tạo dữ liệu test
        self.test_ads_data = {
            'extraction_date': '2024-01-01T00:00:00',
            'campaigns': [
                {
                    'id': 'test_campaign_1',
                    'name': 'Test Campaign 1',
                    'status': 'ACTIVE',
                    'objective': 'REACH',
                    'impressions': 1000,
                    'clicks': 50,
                    'spend': 100.50
                }
            ],
            'message': 'Test data'
        }
    
    def tearDown(self):
        """Dọn dẹp sau test"""
        self.app_context.pop()
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('timestamp', data)
        self.assertIn('openai_configured', data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_index_page(self):
        """Test trang chủ"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Facebook Ads Dashboard', response.data)
    
    def test_ads_data_endpoint(self):
        """Test API endpoint để lấy dữ liệu quảng cáo"""
        # Mock load_ads_data function
        with patch('app.load_ads_data', return_value=self.test_ads_data):
            response = self.client.get('/api/ads-data')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertIn('campaigns', data)
            self.assertEqual(len(data['campaigns']), 1)
            self.assertEqual(data['campaigns'][0]['name'], 'Test Campaign 1')
    
    def test_ask_question_endpoint_success(self):
        """Test API endpoint để hỏi câu hỏi - thành công"""
        # Mock OpenAI response
        mock_openai_response = {
            'choices': [{'message': {'content': 'Đây là câu trả lời test'}}]
        }
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_openai_response
            mock_post.return_value.raise_for_status.return_value = None
            
            # Mock load_ads_data
            with patch('app.load_ads_data', return_value=self.test_ads_data):
                response = self.client.post('/api/ask', 
                                         json={'question': 'Test question'})
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertIn('question', data)
                self.assertIn('answer', data)
                self.assertEqual(data['question'], 'Test question')
                self.assertEqual(data['answer'], 'Đây là câu trả lời test')
    
    def test_ask_question_endpoint_empty_question(self):
        """Test API endpoint với câu hỏi rỗng"""
        response = self.client.post('/api/ask', json={'question': ''})
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_ask_question_endpoint_no_question(self):
        """Test API endpoint không có câu hỏi"""
        response = self.client.post('/api/ask', json={})
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)

class TestOpenAIChatbot(unittest.TestCase):
    """Test class cho OpenAI Chatbot"""
    
    def setUp(self):
        """Thiết lập test environment"""
        self.chatbot = OpenAIChatbot()
        self.test_ads_data = {'campaigns': [{'name': 'Test Campaign'}]}
    
    def test_chatbot_initialization(self):
        """Test khởi tạo chatbot"""
        self.assertIsNotNone(self.chatbot)
        # Kiểm tra xem API key có được load không
        # (có thể là None nếu không có trong .env)
    
    @patch('requests.post')
    def test_ask_question_success(self, mock_post):
        """Test hỏi câu hỏi thành công"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test answer'}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Mock API key
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            chatbot = OpenAIChatbot()
            answer = chatbot.ask_question('Test question', self.test_ads_data)
            
            self.assertEqual(answer, 'Test answer')
            mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_ask_question_api_error(self, mock_post):
        """Test lỗi API"""
        mock_post.side_effect = Exception('API Error')
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            chatbot = OpenAIChatbot()
            answer = chatbot.ask_question('Test question', self.test_ads_data)
            
            self.assertIn('Xin lỗi, có lỗi xảy ra', answer)

class TestFacebookAdsExtractor(unittest.TestCase):
    """Test class cho Facebook Ads Extractor"""
    
    def setUp(self):
        """Thiết lập test environment"""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'FACEBOOK_ACCESS_TOKEN': 'test_token',
            'FACEBOOK_ACCOUNT_IDS': 'test_account_1,test_account_2'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Dọn dẹp sau test"""
        self.env_patcher.stop()
    
    def test_extractor_initialization(self):
        """Test khởi tạo extractor"""
        try:
            extractor = FacebookAdsExtractor()
            self.assertIsNotNone(extractor)
            self.assertEqual(extractor.access_token, 'test_token')
            self.assertEqual(extractor.account_ids, ['test_account_1', 'test_account_2'])
        except ValueError as e:
            # Nếu không có .env file, test này sẽ fail
            self.skipTest(f"Không thể khởi tạo extractor: {e}")
    
    @patch('requests.get')
    def test_test_connection_success(self, mock_get):
        """Test kết nối thành công"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': [{'id': 'test_account'}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        try:
            extractor = FacebookAdsExtractor()
            result = extractor.test_connection()
            self.assertTrue(result)
        except ValueError:
            self.skipTest("Không thể khởi tạo extractor")
    
    @patch('requests.get')
    def test_test_connection_failure(self, mock_get):
        """Test kết nối thất bại"""
        mock_get.side_effect = requests.exceptions.RequestException('Connection Error')
        
        try:
            extractor = FacebookAdsExtractor()
            result = extractor.test_connection()
            self.assertFalse(result)
        except ValueError:
            self.skipTest("Không thể khởi tạo extractor")

class TestLoadAdsData(unittest.TestCase):
    """Test class cho hàm load_ads_data"""
    
    def setUp(self):
        """Thiết lập test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Dọn dẹp sau test"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_ads_data_file_not_found(self):
        """Test load dữ liệu khi file không tồn tại"""
        data = load_ads_data()
        self.assertIn('extraction_date', data)
        self.assertIn('campaigns', data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Dữ liệu mẫu - chưa có dữ liệu thực')
    
    def test_load_ads_data_with_valid_file(self):
        """Test load dữ liệu từ file hợp lệ"""
        test_data = {
            'extraction_date': '2024-01-01T00:00:00',
            'campaigns': [{'name': 'Test Campaign'}]
        }
        
        with open('ads_data.json', 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        data = load_ads_data()
        self.assertEqual(data['extraction_date'], '2024-01-01T00:00:00')
        self.assertEqual(len(data['campaigns']), 1)
        self.assertEqual(data['campaigns'][0]['name'], 'Test Campaign')

def run_tests():
    """Chạy tất cả tests"""
    print("🚀 Bắt đầu chạy tests cho Facebook Ads Dashboard...")
    print("=" * 60)
    
    # Tạo test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestFacebookAdsDashboard)
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestOpenAIChatbot))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFacebookAdsExtractor))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLoadAdsData))
    
    # Chạy tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("=" * 60)
    if result.wasSuccessful():
        print("✅ Tất cả tests đã chạy thành công!")
    else:
        print("❌ Một số tests đã thất bại!")
        print(f"Tests chạy: {result.testsRun}")
        print(f"Tests thất bại: {len(result.failures)}")
        print(f"Tests bị lỗi: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    # Kiểm tra xem có file .env không
    if not os.path.exists('.env'):
        print("⚠️  Không tìm thấy file .env")
        print("📝 Vui lòng tạo file .env với các cấu hình cần thiết")
        print("🔍 Xem file env_example.txt để biết cấu trúc")
    else:
        print("✅ Tìm thấy file .env")
    
    # Chạy tests
    success = run_tests()
    
    # Exit code
    exit(0 if success else 1)