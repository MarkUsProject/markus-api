import abc
import pytest
import markusapi
import datetime
from unittest.mock import patch, PropertyMock, Mock

FAKE_API_KEY = 'fake_api_key'
FAKE_URL = 'http://example.com'


@pytest.fixture
def api():
    return markusapi.Markus(FAKE_API_KEY, FAKE_URL)


class AbstractTestClass(abc.ABC):

    @classmethod
    @pytest.fixture
    def response_mock(cls):
        with patch(f'requests.{cls.request_verb}') as mock:
            type(mock.return_value).ok = PropertyMock(return_value=True)
            mock.return_value.content = 'content'
            mock.return_value.text = 'text'
            mock.return_value.json.return_value = 'json'
            yield mock

    @classmethod
    @pytest.fixture
    def bad_response_mock(cls, response_mock):
        type(response_mock.return_value).ok = PropertyMock(return_value=False)
        yield response_mock

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        pass

    @property
    @abc.abstractmethod
    def request_verb(self):
        pass

    @property
    @abc.abstractmethod
    def response_format(self):
        pass

    @property
    @abc.abstractmethod
    def url(self):
        pass

    def test_json_response_data_on_failure(self, bad_response_mock, basic_call):
        assert basic_call == 'json'

    def test_correct_response_data_on_success(self, response_mock, basic_call):
        assert basic_call == self.response_format

    def test_called_with_correct_athorization(self, response_mock, basic_call):
        assert response_mock.call_args.kwargs['headers']['Authorization'] == f'MarkUsAuth {FAKE_API_KEY}'

    def test_called_with_correct_url(self, response_mock, basic_call):
        assert response_mock.call_args.args[0] == f'{FAKE_URL}/api/{self.url}.json'


class TestGetAllUsers(AbstractTestClass):
    request_verb = 'get'
    response_format = 'json'
    url = 'users'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        return api.get_all_users()


class TestNewUser(AbstractTestClass):
    request_verb = 'post'
    response_format = 'json'
    url = 'users'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        return api.new_user('test', 'Student', 'first', 'last', 'section', '3')

    def test_called_with_basic_params(self, api, response_mock):
        api.new_user('test', 'Student', 'first', 'last')
        params = {"user_name": 'test', "type": 'Student', "first_name": 'first', "last_name": 'last'}
        assert response_mock.call_args.kwargs['params'] == params

    def test_called_with_section(self, api, response_mock):
        api.new_user('test', 'Student', 'first', 'last', section_name='section')
        params = {"user_name": 'test', "type": 'Student', "first_name": 'first', "last_name": 'last', 'section_name': 'section'}
        assert response_mock.call_args.kwargs['params'] == params

    def test_called_with_grace_credits(self, api, response_mock):
        api.new_user('test', 'Student', 'first', 'last', grace_credits='3')
        params = {"user_name": 'test', "type": 'Student', "first_name": 'first', "last_name": 'last', 'grace_credits': '3'}
        assert response_mock.call_args.kwargs['params'] == params


class TestGetAssignments(AbstractTestClass):
    request_verb = 'get'
    response_format = 'json'
    url = 'assignments'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.get_assignments()


class TestGetGroups(AbstractTestClass):
    request_verb = 'get'
    response_format = 'json'
    url = 'assignments/1/groups'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.get_groups(1)


class TestGetGroupsByName(AbstractTestClass):
    request_verb = 'get'
    response_format = 'json'
    url = 'assignments/1/groups/group_ids_by_name'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.get_groups_by_name(1)


class TestGetGroup(AbstractTestClass):
    request_verb = 'get'
    response_format = 'json'
    url = 'assignments/1/groups/1'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.get_group(1, 1)


class TestGetFeedbackFiles(AbstractTestClass):
    request_verb = 'get'
    response_format = 'json'
    url = 'assignments/1/groups/1/feedback_files'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.get_feedback_files(1, 1)


class TestGetFeedbackFile(AbstractTestClass):
    request_verb = 'get'
    response_format = 'content'
    url = 'assignments/1/groups/1/feedback_files/1'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.get_feedback_file(1, 1, 1)


class TestGetGradesSummary(AbstractTestClass):
    request_verb = 'get'
    response_format = 'text'
    url = 'assignments/1/grades_summary'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.get_grades_summary(1)


class TestNewMarksSpreadsheet(AbstractTestClass):
    request_verb = 'post'
    response_format = 'json'
    url = 'grade_entry_forms'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.new_marks_spreadsheet('test', 'description', datetime.datetime.now())

    def test_called_with_basic_params(self, api, response_mock):
        now = datetime.datetime.now()
        api.new_marks_spreadsheet('test', 'description', now)
        params = {
            "short_identifier": 'test',
            "description": 'description',
            "date": now,
            "is_hidden": True,
            "show_total": True,
            "grade_entry_items": None,
        }
        assert response_mock.call_args.kwargs['params'] == params

    def test_called_with_is_hidden(self, api, response_mock):
        now = datetime.datetime.now()
        api.new_marks_spreadsheet('test', 'description', now, is_hidden=False)
        params = {
            "short_identifier": 'test',
            "description": 'description',
            "date": now,
            "is_hidden": False,
            "show_total": True,
            "grade_entry_items": None,
        }
        assert response_mock.call_args.kwargs['params'] == params

    def test_called_with_is_show_total(self, api, response_mock):
        now = datetime.datetime.now()
        api.new_marks_spreadsheet('test', 'description', now, show_total=False)
        params = {
            "short_identifier": 'test',
            "description": 'description',
            "date": now,
            "is_hidden": True,
            "show_total": False,
            "grade_entry_items": None,
        }
        assert response_mock.call_args.kwargs['params'] == params

    def test_called_with_is_show_grade_entry_items(self, api, response_mock):
        now = datetime.datetime.now()
        ge_items = [{'name': 'a', 'out_of': 4}]
        api.new_marks_spreadsheet('test', 'description', now, grade_entry_items=ge_items)
        params = {
            "short_identifier": 'test',
            "description": 'description',
            "date": now,
            "is_hidden": True,
            "show_total": True,
            "grade_entry_items": ge_items,
        }
        assert response_mock.call_args.kwargs['params'] == params


class TestUpdateMarksSpreadsheet(AbstractTestClass):
    request_verb = 'put'
    response_format = 'json'
    url = 'grade_entry_forms/1'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.update_marks_spreadsheet(1, 'test', 'description', datetime.datetime.now())

    def test_called_with_basic_params(self, api, response_mock):
        now = datetime.datetime.now()
        api.update_marks_spreadsheet(1, 'test', 'description', now)
        params = {
            "short_identifier": 'test',
            "description": 'description',
            "date": now
        }
        assert response_mock.call_args.kwargs['params'] == params

    def test_called_with_is_hidden(self, api, response_mock):
        now = datetime.datetime.now()
        api.update_marks_spreadsheet(1, 'test', 'description', now, is_hidden=False)
        params = {
            "short_identifier": 'test',
            "description": 'description',
            "date": now,
            "is_hidden": False
        }
        assert response_mock.call_args.kwargs['params'] == params

    def test_called_with_is_show_total(self, api, response_mock):
        now = datetime.datetime.now()
        api.update_marks_spreadsheet(1, 'test', 'description', now, show_total=False)
        params = {
            "short_identifier": 'test',
            "description": 'description',
            "date": now,
            "show_total": False
        }
        assert response_mock.call_args.kwargs['params'] == params

    def test_called_with_is_show_grade_entry_items(self, api, response_mock):
        now = datetime.datetime.now()
        ge_items = [{'name': 'a', 'out_of': 4}]
        api.update_marks_spreadsheet(1, 'test', 'description', now, grade_entry_items=ge_items)
        params = {
            "short_identifier": 'test',
            "description": 'description',
            "date": now,
            "grade_entry_items": ge_items,
        }
        assert response_mock.call_args.kwargs['params'] == params


class TestUpdateMarksSpreadsheetGrades(AbstractTestClass):
    request_verb = 'put'
    response_format = 'json'
    url = 'grade_entry_forms/1/update_grades'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.update_marks_spreadsheets_grades(1, 'some_user', {'some_column': 2})

    def test_called_with_basic_params(self, api, response_mock):
        api.update_marks_spreadsheets_grades(1, 'some_user', {'some_column': 2})
        params = {
            "user_name": 'some_user',
            "grade_entry_items": {'some_column': 2}
        }
        assert response_mock.call_args.kwargs['json'] == params


class TestGetMarksSpreadsheets(AbstractTestClass):
    request_verb = 'get'
    response_format = 'json'
    url = 'grade_entry_forms'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.get_marks_spreadsheets()


class TestGetMarksSpreadsheet(AbstractTestClass):
    request_verb = 'get'
    response_format = 'text'
    url = 'grade_entry_forms/1'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.get_marks_spreadsheet(1)


class TestUploadFeedbackFileReplace(AbstractTestClass):
    request_verb = 'put'
    response_format = 'json'
    url = 'assignments/1/groups/1/feedback_files/1'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        api.get_feedback_files = Mock(return_value=[{'id': 1, 'filename': 'test.txt'}])
        yield api.upload_feedback_file(1, 1, 'test.txt', 'feedback info')

    def test_discovers_mime_type(self, api, response_mock):
        api.get_feedback_files = Mock(return_value=[{'id': 1, 'filename': 'test.txt'}])
        api.upload_feedback_file(1, 1, 'test.txt', 'feedback info')
        assert response_mock.call_args.kwargs['params']["mime_type"] == 'text/plain'

    def test_called_with_mime_type(self, api, response_mock):
        api.get_feedback_files = Mock(return_value=[{'id': 1, 'filename': 'test.txt'}])
        api.upload_feedback_file(1, 1, 'test.txt', 'feedback info', mime_type='application/octet-stream')
        params = {"filename": 'test.txt', "mime_type": 'application/octet-stream'}
        assert response_mock.call_args.kwargs['params'] == params

    def test_sends_file_data(self, api, response_mock):
        api.get_feedback_files = Mock(return_value=[{'id': 1, 'filename': 'test.txt'}])
        api.upload_feedback_file(1, 1, 'test.txt', 'feedback info')
        files = {"file_content": ('test.txt', 'feedback info')}
        assert response_mock.call_args.kwargs['files'] == files


class TestUploadFeedbackFileNew(AbstractTestClass):
    request_verb = 'post'
    response_format = 'json'
    url = 'assignments/1/groups/1/feedback_files'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        api.get_feedback_files = Mock(return_value=[{'id': 1, 'filename': 'other.txt'}])
        yield api.upload_feedback_file(1, 1, 'test.txt', 'feedback info')


class TestUploadFeedbackFileNoOverwrite(TestUploadFeedbackFileNew):
    @staticmethod
    @pytest.fixture
    def basic_call(api):
        api.get_feedback_files = Mock(return_value=[{'id': 1, 'filename': 'test.txt'}])
        yield api.upload_feedback_file(1, 1, 'test.txt', 'feedback info', overwrite=False)


class TestUploadTestGroupResultsJsonString(AbstractTestClass):
    request_verb = 'post'
    response_format = 'json'
    url = 'assignments/1/groups/1/test_group_results'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.upload_test_group_results(1, 1, 1, '{"data": []}')

    def test_called_wth_basic_args(self, api, response_mock):
        api.upload_test_group_results(1, 1, 1, '{"data": []}')
        params = {"test_run_id": 1, "test_output": '{"data": []}'}
        assert response_mock.call_args.kwargs['json'] == params


class TestUploadTestGroupResultsDict(AbstractTestClass):
    request_verb = 'post'
    response_format = 'json'
    url = 'assignments/1/groups/1/test_group_results'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.upload_test_group_results(1, 1, 1, {"data": []})

    def test_dict_changed_to_json_string(self, api, response_mock):
        api.upload_test_group_results(1, 1, 1, {"data": []})
        assert response_mock.call_args.kwargs['json']["test_output"] == '{"data": []}'


class TestUploadAnnotations(AbstractTestClass):
    request_verb = 'post'
    response_format = 'json'
    url = 'assignments/1/groups/1/add_annotations'
    annotations = [{
        "filename": 'test.txt',
        "annotation_category_name": "category",
        "content": "something",
        "line_start": 1,
        "line_end": 2,
        "column_start": 3,
        "column_end": 10,
    }]

    @classmethod
    @pytest.fixture
    def basic_call(cls, api):
        yield api.upload_annotations(1, 1, cls.annotations)

    def test_called_with_basic_params(self, api, response_mock):
        api.upload_annotations(1, 1, self.annotations)
        params = {"annotations": self.annotations, "force_complete": False}
        assert response_mock.call_args.kwargs['json'] == params

    def test_called_with_force_complete(self, api, response_mock):
        api.upload_annotations(1, 1, self.annotations, True)
        params = {"annotations": self.annotations, "force_complete": True}
        assert response_mock.call_args.kwargs['json'] == params


class TestGetAnnotations(AbstractTestClass):
    request_verb = 'get'
    response_format = 'json'
    url = 'assignments/1/groups/1/annotations'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.get_annotations(1, 1)


class TestUpdateMarksSingleGroup(AbstractTestClass):
    request_verb = 'put'
    response_format = 'json'
    url = 'assignments/1/groups/1/update_marks'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.update_marks_single_group({"criteria_a": 10}, 1, 1)

    def test_called_with_basic_params(self, api, response_mock):
        api.update_marks_single_group({"criteria_a": 10}, 1, 1)
        assert response_mock.call_args.kwargs['json'] == {"criteria_a": 10}


class TestUpdateMarkingState(AbstractTestClass):
    request_verb = 'put'
    response_format = 'json'
    url = 'assignments/1/groups/1/update_marking_state'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.update_marking_state(1, 1, 'collected')

    def test_called_with_basic_params(self, api, response_mock):
        api.update_marking_state(1, 1, 'collected')
        assert response_mock.call_args.kwargs['params'] == {"marking_state": 'collected'}


class TestCreateExtraMarks(AbstractTestClass):
    request_verb = 'post'
    response_format = 'json'
    url = 'assignments/1/groups/1/create_extra_marks'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.create_extra_marks(1, 1, 10, 'a bonus!')

    def test_called_with_basic_params(self, api, response_mock):
        api.create_extra_marks(1, 1, 10, 'a bonus!')
        assert response_mock.call_args.kwargs['params'] == {"extra_marks": 10, "description": 'a bonus!'}


class TestRemoveExtraMarks(AbstractTestClass):
    request_verb = 'delete'
    response_format = 'json'
    url = 'assignments/1/groups/1/remove_extra_marks'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.remove_extra_marks(1, 1, 10, 'a bonus!')

    def test_called_with_basic_params(self, api, response_mock):
        api.remove_extra_marks(1, 1, 10, 'a bonus!')
        assert response_mock.call_args.kwargs['params'] == {"extra_marks": 10, "description": 'a bonus!'}


class TestGetFilesFromRepo(AbstractTestClass):
    request_verb = 'get'
    response_format = 'content'
    url = 'assignments/1/groups/1/submission_files'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.get_files_from_repo(1, 1)

    def test_called_with_basic_params(self, api, response_mock):
        api.get_files_from_repo(1, 1)
        assert response_mock.call_args.kwargs['params'] == {"collected": True}

    def test_called_with_collected(self, api, response_mock):
        api.get_files_from_repo(1, 1, collected=False)
        assert response_mock.call_args.kwargs['params'] == {}

    def test_called_with_filename(self, api, response_mock):
        api.get_files_from_repo(1, 1, filename='test.txt')
        assert response_mock.call_args.kwargs['params'] == {"collected": True, "filename": 'test.txt'}


class TestUploadFolderToRepo(AbstractTestClass):
    request_verb = 'post'
    response_format = 'json'
    url = 'assignments/1/groups/1/submission_files/create_folders'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.upload_folder_to_repo(1, 1, 'subdir')

    def test_called_with_basic_params(self, api, response_mock):
        api.upload_folder_to_repo(1, 1, 'subdir')
        assert response_mock.call_args.kwargs['params'] == {"folder_path": 'subdir'}


class TestUploadFileToRepo(AbstractTestClass):
    request_verb = 'post'
    response_format = 'json'
    url = 'assignments/1/groups/1/submission_files'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.upload_file_to_repo(1, 1, 'test.txt', 'some content')

    def test_discovers_mime_type(self, api, response_mock):
        api.upload_file_to_repo(1, 1, 'test.txt', 'some content')
        assert response_mock.call_args.kwargs['params']["mime_type"] == 'text/plain'

    def test_called_with_mime_type(self, api, response_mock):
        api.upload_file_to_repo(1, 1, 'test.txt', 'feedback info', mime_type='application/octet-stream')
        params = {"filename": 'test.txt', "mime_type": 'application/octet-stream'}
        assert response_mock.call_args.kwargs['params'] == params

    def test_sends_file_data(self, api, response_mock):
        api.upload_file_to_repo(1, 1, 'test.txt', 'some content')
        files = {"file_content": ('test.txt', 'some content')}
        assert response_mock.call_args.kwargs['files'] == files


class TestRemoveFileFromRepo(AbstractTestClass):
    request_verb = 'delete'
    response_format = 'json'
    url = 'assignments/1/groups/1/submission_files/remove_file'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.remove_file_from_repo(1, 1, 'test.txt')

    def test_called_with_basic_params(self, api, response_mock):
        api.remove_file_from_repo(1, 1, 'test.txt')
        assert response_mock.call_args.kwargs['params'] == {"filename": 'test.txt'}


class TestRemoveFolderFromRepo(AbstractTestClass):
    request_verb = 'delete'
    response_format = 'json'
    url = 'assignments/1/groups/1/submission_files/remove_folder'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.remove_folder_from_repo(1, 1, 'subdir')

    def test_called_with_basic_params(self, api, response_mock):
        api.remove_folder_from_repo(1, 1, 'subdir')
        assert response_mock.call_args.kwargs['params'] == {"folder_path": 'subdir'}


class TestGetTestSpecs(AbstractTestClass):
    request_verb = 'get'
    response_format = 'json'
    url = 'assignments/1/test_specs'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.get_test_specs(1)


class TestUpdateTestSpecs(AbstractTestClass):
    request_verb = 'post'
    response_format = 'json'
    url = 'assignments/1/update_test_specs'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.update_test_specs(1, {})

    def test_called_with_basic_params(self, api, response_mock):
        specs = {'some': ['fake', 'data']}
        api.update_test_specs(1, specs)
        assert response_mock.call_args.kwargs['json'] == {"specs": specs}


class TestGetTestFiles(AbstractTestClass):
    request_verb = 'get'
    response_format = 'content'
    url = 'assignments/1/test_files'

    @staticmethod
    @pytest.fixture
    def basic_call(api):
        yield api.get_test_files(1)
