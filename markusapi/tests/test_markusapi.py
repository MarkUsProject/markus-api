import pytest
import typing
import mimetypes
import json
import http.client
from hypothesis import given
from hypothesis import strategies as st
from unittest.mock import patch
from functools import wraps
from markusapi import Markus

def strategies_from_signature(method):
    mapping = {k:st.from_type(v) for k,v in typing.get_type_hints(method).items() if k != 'return'}
    return st.fixed_dictionaries(mapping)

def dummy_markus(scheme='http'):
    return Markus('',f'{scheme}://localhost:8080')

DUMMY_RETURNS = {
    "submit_request": b'{"f": "foo"}',
    "decode_json_response": {'f': 'foo'},
    "decode_text_response": '{"f": "foo"}',
    "path": '/fake/path'
}

def file_name_strategy():
    exts = '|'.join([f'\\{ext}' for ext in mimetypes.types_map.keys()])
    return st.from_regex(fr'\w+({exts})', fullmatch=True)

class TestMarkusAPICalls:

    def test_init_set_attributes(self):
        obj = dummy_markus()
        assert isinstance(obj, Markus)

    def test_init_bad_scheme(self):
        try:
            obj = dummy_markus('ftp')
        except AssertionError:
            return
        pytest.fail()

    def test_init_parse_url(self):
        api_key = ''
        url = 'https://markus.com/api/users?id=1'
        obj = Markus(api_key, url)
        assert obj.parsed_url.scheme == 'https'
        assert obj.parsed_url.netloc == 'markus.com'
        assert obj.parsed_url.path == '/api/users'
        assert obj.parsed_url.query == 'id=1'

    @given(kwargs=strategies_from_signature(Markus.get_all_users))
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'decode_json_response')
    def test_get_all_users(self, decode_json_response, submit_request, kwargs):
        dummy_markus().get_all_users(**kwargs)
        submit_request.assert_called_with(None, '/api/users.json', 'GET')
        decode_json_response.assert_called_with(submit_request.return_value)

    @given(kwargs=strategies_from_signature(Markus.new_user))
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    def test_new_user(self, submit_request, kwargs):
        dummy_markus().new_user(**kwargs)
        submit_request.assert_called_once()
        call_args = submit_request.call_args[0][0].values()
        assert all(v in call_args for k,v in kwargs.items() if v is not None)

    @given(kwargs=strategies_from_signature(Markus.get_assignments))
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'decode_json_response')
    def test_get_assignments(self, decode_json_response, submit_request, kwargs):
        dummy_markus().get_assignments(**kwargs)
        submit_request.assert_called_with(None, '/api/assignments.json', 'GET')
        decode_json_response.assert_called_with(submit_request.return_value)    

    @given(kwargs=strategies_from_signature(Markus.get_groups))
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'decode_json_response')
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_get_groups(self, get_path, decode_json_response, submit_request, kwargs):
        dummy_markus().get_groups(**kwargs)
        get_path.assert_called_with(assignments=kwargs['assignment_id'], groups=None)
        submit_request.assert_called_with(None, f'{get_path.return_value}.json', 'GET')
        decode_json_response.assert_called_with(submit_request.return_value)   

    @given(kwargs=strategies_from_signature(Markus.get_groups_by_name))
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'decode_json_response')
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_get_groups_by_name(self, get_path, decode_json_response, submit_request, kwargs):
        dummy_markus().get_groups_by_name(**kwargs)
        get_path.assert_called_with(assignments=kwargs['assignment_id'], groups=None, group_ids_by_name=None)
        submit_request.assert_called_with(None, f'{get_path.return_value}.json', 'GET')
        decode_json_response.assert_called_with(submit_request.return_value)   

    @given(kwargs=strategies_from_signature(Markus.get_group))
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'decode_json_response')
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_get_group(self, get_path, decode_json_response, submit_request, kwargs):
        dummy_markus().get_group(**kwargs)
        get_path.assert_called_with(assignments=kwargs['assignment_id'], groups=kwargs['group_id'])
        submit_request.assert_called_with(None, f'{get_path.return_value}.json', 'GET')
        decode_json_response.assert_called_with(submit_request.return_value)  

    @given(kwargs=strategies_from_signature(Markus.get_feedback_files))
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'decode_json_response')
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_get_feedback_files(self, get_path, decode_json_response, submit_request, kwargs):
        dummy_markus().get_feedback_files(**kwargs)
        get_path.assert_called_with(assignments=kwargs['assignment_id'], groups=kwargs['group_id'], feedback_files=None)
        submit_request.assert_called_with({}, f'{get_path.return_value}.json', 'GET')
        decode_json_response.assert_called_with(submit_request.return_value)  

    @given(kwargs=strategies_from_signature(Markus.get_feedback_file))
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'decode_text_response')
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_get_feedback_file(self, get_path, decode_text_response, submit_request, kwargs):
        dummy_markus().get_feedback_file(**kwargs)
        get_path.assert_called_with(assignments=kwargs['assignment_id'], groups=kwargs['group_id'], feedback_files=kwargs['feedback_file_id'])
        submit_request.assert_called_with({}, f'{get_path.return_value}.json', 'GET')
        decode_text_response.assert_called_with(submit_request.return_value) 

    @given(kwargs=strategies_from_signature(Markus.get_grades_summary))
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'decode_text_response')
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_get_grades_summary(self, get_path, decode_text_response, submit_request, kwargs):
        dummy_markus().get_grades_summary(**kwargs)
        get_path.get_grades_summary(assignments=kwargs['assignment_id'], grades_summary=None)
        submit_request.assert_called_with({}, f'{get_path.return_value}.json', 'GET')
        decode_text_response.assert_called_with(submit_request.return_value)        

    @given(kwargs=strategies_from_signature(Markus.update_marks_spreadsheets_grades))
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_update_marks_spreadsheets_grades(self, get_path, submit_request, kwargs):
        dummy_markus().update_marks_spreadsheets_grades(**kwargs)
        get_path.assert_called_with(grade_entry_forms=kwargs['spreadsheet_id'], update_grades=None)
        params = {'user_name': kwargs['user_name'], 'grade_entry_items': kwargs['grades_per_column']}
        submit_request.assert_called_with(params, get_path.return_value + '.json', 'PUT', content_type='application/json')

    @given(kwargs=strategies_from_signature(Markus.get_marks_spreadsheets))
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'decode_json_response', return_value=[DUMMY_RETURNS['decode_json_response']])
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_get_marks_spreadsheets(self, get_path, decode_json_response, submit_request, kwargs):
        dummy_markus().get_marks_spreadsheets(**kwargs)
        get_path.assert_called_with(grade_entry_forms=None)
        submit_request.assert_called_with({}, f'{get_path.return_value}.json', 'GET')
        decode_json_response.assert_called_with(submit_request.return_value)        

    @given(kwargs=strategies_from_signature(Markus.get_marks_spreadsheet))
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'decode_text_response')
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_get_marks_spreadsheet(self, get_path, decode_text_response, submit_request, kwargs):
        dummy_markus().get_marks_spreadsheet(**kwargs)
        get_path.assert_called_with(grade_entry_forms=kwargs['spreadsheet_id'])
        submit_request.assert_called_with({}, f'{get_path.return_value}.json', 'GET')
        decode_text_response.assert_called_with(submit_request.return_value) 

    @given(kwargs=strategies_from_signature(Markus.upload_feedback_file), filename=file_name_strategy())
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'decode_json_response', return_value=[DUMMY_RETURNS['decode_json_response']])
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_upload_feedback_file_good_title(self, get_path, decode_json_response, submit_request, kwargs, filename):
        dummy_markus().upload_feedback_file(**{**kwargs, 'title': filename})
        get_path.assert_called_with(assignments=kwargs['assignment_id'], groups=kwargs['group_id'], feedback_files=None)
        params, path, request_type, _content_type  = submit_request.call_args[0]
        assert path == get_path.return_value
        assert params.keys() == {'filename', 'file_content', 'mime_type'}

    @given(kwargs=strategies_from_signature(Markus.upload_feedback_file), filename=file_name_strategy())
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_upload_feedback_file_overwrite(self, get_path, submit_request, kwargs, filename):
        with patch.object(Markus, 'decode_json_response', return_value=[{'id': 1, 'filename': filename}]):  
            dummy_markus().upload_feedback_file(**{**kwargs, 'title': filename})          
            _params, _path, request_type, _content_type  = submit_request.call_args[0]
            assert request_type == ('PUT' if kwargs['overwrite'] else 'POST')

    @given(kwargs=strategies_from_signature(Markus.upload_feedback_file), filename=st.from_regex(r'\w+', fullmatch=True))
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'decode_json_response',  return_value=[DUMMY_RETURNS['decode_json_response']])
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_upload_feedback_file_bad_title(self, get_path, decode_json_response, submit_request, kwargs, filename):
        try:
            dummy_markus().upload_feedback_file(**{**kwargs, 'title': filename, 'mime_type': None})
        except ValueError:
            return
        pytest.fail()

    @given(kwargs=strategies_from_signature(Markus.upload_test_group_results))
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_upload_test_group_results(self, get_path, submit_request, kwargs):
        dummy_markus().upload_test_group_results(**kwargs)
        params = {
            'test_run_id': kwargs['test_run_id'],
            'test_output': kwargs['test_output']
        }
        get_path.assert_called_with(assignments=kwargs['assignment_id'], groups=kwargs['group_id'], test_group_results=None)
        submit_request.assert_called_with(params, get_path.return_value, 'POST')

    @given(kwargs=strategies_from_signature(Markus.upload_annotations))
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_upload_annotations(self, get_path, submit_request, kwargs):
        dummy_markus().upload_annotations(**kwargs)
        params = {
            'annotations': kwargs['annotations'],
            'force_complete': kwargs['force_complete']
        }
        get_path.assert_called_with(assignments=kwargs['assignment_id'], groups=kwargs['group_id'], add_annotations=None)
        submit_request.assert_called_with(params, get_path.return_value, 'POST', 'application/json')

    @given(kwargs=strategies_from_signature(Markus.get_annotations))
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'decode_json_response')
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_get_annotations(self, get_path, decode_json_response, submit_request, kwargs):
        dummy_markus().get_annotations(**kwargs)
        get_path.assert_called_with(assignments=kwargs['assignment_id'], groups=kwargs['group_id'], annotations=None)
        submit_request.assert_called_with(None, f'{get_path.return_value}.json', 'GET')
        decode_json_response.assert_called_with(submit_request.return_value)

    @given(kwargs=strategies_from_signature(Markus.update_marks_single_group))
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_update_marks_single_group(self, get_path, submit_request, kwargs):
        dummy_markus().update_marks_single_group(**kwargs)
        get_path.assert_called_with(assignments=kwargs['assignment_id'], groups=kwargs['group_id'], update_marks=None)
        submit_request.assert_called_with(kwargs['criteria_mark_map'], get_path.return_value, 'PUT')

    @given(kwargs=strategies_from_signature(Markus.upload_file_to_repo), filename=file_name_strategy())
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'decode_json_response', return_value=[DUMMY_RETURNS['decode_json_response']])
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_upload_file_to_repo(self, get_path, decode_json_response, submit_request, kwargs, filename):
        dummy_markus().upload_file_to_repo(**{**kwargs, 'file_path': filename})
        get_path.assert_called_with(assignments=kwargs['assignment_id'], groups=kwargs['group_id'], submission_files=None)
        params, path, request_type, _content_type  = submit_request.call_args[0]
        assert path == get_path.return_value
        assert params.keys() == {'filename', 'file_content', 'mime_type'}

    @given(kwargs=strategies_from_signature(Markus.remove_file_from_repo), filename=file_name_strategy())
    @patch.object(Markus, 'submit_request', return_value=DUMMY_RETURNS['submit_request'])
    @patch.object(Markus, 'decode_json_response', return_value=[DUMMY_RETURNS['decode_json_response']])
    @patch.object(Markus, 'get_path', return_value=DUMMY_RETURNS['path'])
    def test_remove_file_from_repo(self, get_path, decode_json_response, submit_request, kwargs, filename):
        dummy_markus().remove_file_from_repo(**{**kwargs, 'file_path': filename})
        get_path.assert_called_with(assignments=kwargs['assignment_id'], groups=kwargs['group_id'], submission_files=None, remove_file=None)
        params, path, request_type  = submit_request.call_args[0]
        assert path == get_path.return_value
        assert params.keys() == {'filename'}

class TestMarkusAPIHelpers:

    @given(kwargs=strategies_from_signature(Markus.submit_request),
           content_type=st.sampled_from(['application/x-www-form-urlencoded', 'application/json']))
    @patch.object(Markus, '_do_submit_request')
    def test_submit_request_check_types(self, do_submit_request, kwargs, content_type):
        dummy_markus().submit_request(**{**kwargs, 'content_type': content_type})
        params, _path, _request_type, headers = do_submit_request.call_args[0]
        assert isinstance(params, (str, type(None)))
        assert isinstance(headers, dict)

    @given(kwargs=strategies_from_signature(Markus.submit_request),
           content_type=st.sampled_from(['multipart/form-data', 'bad/content/type']))
    @patch.object(Markus, '_do_submit_request')
    def test_submit_request_check_catches_invalid(self, do_submit_request, kwargs, content_type):
        try:
            dummy_markus().submit_request(**{**kwargs, 'content_type': content_type})
        except ValueError:
            return
        params, _path, _request_type, headers = do_submit_request.call_args[0]
        assert isinstance(params, (str, type(None)))

    @given(kwargs=strategies_from_signature(Markus._do_submit_request))
    @patch.object(http.client.HTTPConnection, 'request')
    @patch.object(http.client.HTTPConnection, 'getresponse')
    @patch.object(http.client.HTTPConnection, 'close')
    def test__do_submit_request_http(self, request, getresponse, close, kwargs):
        dummy_markus('http')._do_submit_request(**kwargs)
        request.assert_called_once()
        getresponse.assert_called_once()
        close.assert_called_once()
        
    @given(kwargs=strategies_from_signature(Markus._do_submit_request))
    @patch.object(http.client.HTTPSConnection, 'request')
    @patch.object(http.client.HTTPSConnection, 'getresponse')
    @patch.object(http.client.HTTPSConnection, 'close')
    def test__do_submit_request_https(self, request, getresponse, close, kwargs):
        dummy_markus('https')._do_submit_request(**kwargs)
        request.assert_called_once()
        getresponse.assert_called_once()
        close.assert_called_once()

    @given(kwargs=st.dictionaries(st.text(), st.text()))
    def test_get_path(self, kwargs):
        path = Markus.get_path(**kwargs)
        for k,v in kwargs.items():
            assert k + (f'/{v}' if v is not None else '') in path 

    @given(strategies_from_signature(Markus.decode_text_response))
    def test_decode_text_response(self, **kwargs):
        result = Markus.decode_text_response(**kwargs)
        assert isinstance(result, str)

    @given(in_dict=st.dictionaries(st.text(), st.text()))
    def test_decode_text_response(self, in_dict):
        res = json.dumps(in_dict).encode()
        result = Markus.decode_text_response(['', '', res])
        assert isinstance(result, str)

