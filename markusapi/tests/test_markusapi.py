import pytest
import typing
import mimetypes
import json
import http.client
from hypothesis import given
from hypothesis import strategies as st
from unittest.mock import patch
from markusapi import Markus


def strategies_from_signature(method):
    mapping = {k: st.from_type(v) for k, v in typing.get_type_hints(method).items() if k != "return"}
    return st.fixed_dictionaries(mapping)


def dummy_markus(scheme="http"):
    return Markus("", f"{scheme}://localhost:8080")


DUMMY_RETURNS = {
    "_submit_request": b'{"f": "foo"}',
    "_decode_json_response": {"f": "foo"},
    "_decode_text_response": '{"f": "foo"}',
    "path": "/fake/path",
}


def file_name_strategy():
    exts = "|".join([f"\\{ext}" for ext in mimetypes.types_map.keys()])
    return st.from_regex(fr"\w+({exts})", fullmatch=True)


class TestMarkusAPICalls:
    def test_init_set_attributes(self):
        obj = dummy_markus()
        assert isinstance(obj, Markus)

    def test_init_bad_scheme(self):
        try:
            dummy_markus("ftp")
        except AssertionError:
            return
        pytest.fail()

    def test_init_parse_url(self):
        api_key = ""
        url = "https://markus.com/api/users?id=1"
        obj = Markus(api_key, url)
        assert obj.parsed_url.scheme == "https"
        assert obj.parsed_url.netloc == "markus.com"
        assert obj.parsed_url.path == "/api/users"
        assert obj.parsed_url.query == "id=1"

    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_json_response")
    def test_get_all_users(self, _decode_json_response, _submit_request):
        dummy_markus().get_all_users()
        _submit_request.assert_called_with(None, "/api/users.json", "GET")
        _decode_json_response.assert_called_with(_submit_request.return_value)

    @given(kwargs=strategies_from_signature(Markus.new_user))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    def test_new_user(self, _submit_request, kwargs):
        dummy_markus().new_user(**kwargs)
        _submit_request.assert_called_once()
        call_args = _submit_request.call_args[0][0].values()
        assert all(v in call_args for k, v in kwargs.items() if v is not None)

    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_json_response")
    def test_get_assignments(self, _decode_json_response, _submit_request):
        dummy_markus().get_assignments()
        _submit_request.assert_called_with(None, "/api/assignments.json", "GET")
        _decode_json_response.assert_called_with(_submit_request.return_value)

    @given(kwargs=strategies_from_signature(Markus.get_groups))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_json_response")
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_get_groups(self, _get_path, _decode_json_response, _submit_request, kwargs):
        dummy_markus().get_groups(**kwargs)
        _get_path.assert_called_with(assignments=kwargs["assignment_id"], groups=None)
        _submit_request.assert_called_with(None, f"{_get_path.return_value}.json", "GET")
        _decode_json_response.assert_called_with(_submit_request.return_value)

    @given(kwargs=strategies_from_signature(Markus.get_groups_by_name))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_json_response")
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_get_groups_by_name(self, _get_path, _decode_json_response, _submit_request, kwargs):
        dummy_markus().get_groups_by_name(**kwargs)
        _get_path.assert_called_with(assignments=kwargs["assignment_id"], groups=None, group_ids_by_name=None)
        _submit_request.assert_called_with(None, f"{_get_path.return_value}.json", "GET")
        _decode_json_response.assert_called_with(_submit_request.return_value)

    @given(kwargs=strategies_from_signature(Markus.get_group))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_json_response")
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_get_group(self, _get_path, _decode_json_response, _submit_request, kwargs):
        dummy_markus().get_group(**kwargs)
        _get_path.assert_called_with(assignments=kwargs["assignment_id"], groups=kwargs["group_id"])
        _submit_request.assert_called_with(None, f"{_get_path.return_value}.json", "GET")
        _decode_json_response.assert_called_with(_submit_request.return_value)

    @given(kwargs=strategies_from_signature(Markus.get_feedback_files))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_json_response")
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_get_feedback_files(self, _get_path, _decode_json_response, _submit_request, kwargs):
        dummy_markus().get_feedback_files(**kwargs)
        _get_path.assert_called_with(
            assignments=kwargs["assignment_id"], groups=kwargs["group_id"], feedback_files=None
        )
        _submit_request.assert_called_with({}, f"{_get_path.return_value}.json", "GET")
        _decode_json_response.assert_called_with(_submit_request.return_value)

    @given(kwargs=strategies_from_signature(Markus.get_feedback_file))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_text_response")
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_get_feedback_file(self, _get_path, _decode_text_response, _submit_request, kwargs):
        dummy_markus().get_feedback_file(**kwargs)
        _get_path.assert_called_with(
            assignments=kwargs["assignment_id"], groups=kwargs["group_id"], feedback_files=kwargs["feedback_file_id"]
        )
        _submit_request.assert_called_with({}, f"{_get_path.return_value}.json", "GET")
        _decode_text_response.assert_called_with(_submit_request.return_value)

    @given(kwargs=strategies_from_signature(Markus.get_grades_summary))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_text_response")
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_get_grades_summary(self, _get_path, _decode_text_response, _submit_request, kwargs):
        dummy_markus().get_grades_summary(**kwargs)
        _get_path.get_grades_summary(assignments=kwargs["assignment_id"], grades_summary=None)
        _submit_request.assert_called_with({}, f"{_get_path.return_value}.json", "GET")
        _decode_text_response.assert_called_with(_submit_request.return_value)

    @given(kwargs=strategies_from_signature(Markus.new_marks_spreadsheet))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_new_marks_spreadsheet(self, _get_path, _submit_request, kwargs):
        dummy_markus().new_marks_spreadsheet(**kwargs)
        _get_path.assert_called_with(grade_entry_forms=None)
        params = {
            "short_identifier": kwargs["short_identifier"],
            "description": kwargs["description"],
            "date": kwargs["date"],
            "is_hidden": kwargs["is_hidden"],
            "show_total": kwargs["show_total"],
            "grade_entry_items": kwargs["grade_entry_items"],
        }
        _submit_request.assert_called_with(
            params, _get_path.return_value + ".json", "POST", content_type="application/json"
        )

    @given(kwargs=strategies_from_signature(Markus.update_marks_spreadsheet))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_update_marks_spreadsheet(self, _get_path, _submit_request, kwargs):
        dummy_markus().update_marks_spreadsheet(**kwargs)
        _get_path.assert_called_with(grade_entry_forms=kwargs["spreadsheet_id"])
        params = {
            "short_identifier": kwargs["short_identifier"],
            "description": kwargs["description"],
            "date": kwargs["date"],
            "is_hidden": kwargs["is_hidden"],
            "show_total": kwargs["show_total"],
            "grade_entry_items": kwargs["grade_entry_items"],
        }
        for name in list(params):
            if params[name] is None:
                params.pop(name)
        _submit_request.assert_called_with(
            params, _get_path.return_value + ".json", "PUT", content_type="application/json"
        )

    @given(kwargs=strategies_from_signature(Markus.update_marks_spreadsheets_grades))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_update_marks_spreadsheets_grades(self, _get_path, _submit_request, kwargs):
        dummy_markus().update_marks_spreadsheets_grades(**kwargs)
        _get_path.assert_called_with(grade_entry_forms=kwargs["spreadsheet_id"], update_grades=None)
        params = {"user_name": kwargs["user_name"], "grade_entry_items": kwargs["grades_per_column"]}
        _submit_request.assert_called_with(
            params, _get_path.return_value + ".json", "PUT", content_type="application/json"
        )

    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_json_response", return_value=[DUMMY_RETURNS["_decode_json_response"]])
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_get_marks_spreadsheets(self, _get_path, _decode_json_response, _submit_request):
        dummy_markus().get_marks_spreadsheets()
        _get_path.assert_called_with(grade_entry_forms=None)
        _submit_request.assert_called_with({}, f"{_get_path.return_value}.json", "GET")
        _decode_json_response.assert_called_with(_submit_request.return_value)

    @given(kwargs=strategies_from_signature(Markus.get_marks_spreadsheet))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_text_response")
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_get_marks_spreadsheet(self, _get_path, _decode_text_response, _submit_request, kwargs):
        dummy_markus().get_marks_spreadsheet(**kwargs)
        _get_path.assert_called_with(grade_entry_forms=kwargs["spreadsheet_id"])
        _submit_request.assert_called_with({}, f"{_get_path.return_value}.json", "GET")
        _decode_text_response.assert_called_with(_submit_request.return_value)

    @given(kwargs=strategies_from_signature(Markus.upload_feedback_file), filename=file_name_strategy())
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_json_response", return_value=[DUMMY_RETURNS["_decode_json_response"]])
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_upload_feedback_file_good_title(self, _get_path, _decode_json_response, _submit_request, kwargs, filename):
        dummy_markus().upload_feedback_file(**{**kwargs, "title": filename})
        _get_path.assert_called_with(
            assignments=kwargs["assignment_id"], groups=kwargs["group_id"], feedback_files=None
        )
        params, path, request_type, _content_type = _submit_request.call_args[0]
        assert path == _get_path.return_value
        assert params.keys() == {"filename", "file_content", "mime_type"}

    @given(kwargs=strategies_from_signature(Markus.upload_feedback_file), filename=file_name_strategy())
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_upload_feedback_file_overwrite(self, _get_path, _submit_request, kwargs, filename):
        with patch.object(Markus, "_decode_json_response", return_value=[{"id": 1, "filename": filename}]):
            dummy_markus().upload_feedback_file(**{**kwargs, "title": filename})
            _get_path.assert_called_with(
                assignments=kwargs["assignment_id"], groups=kwargs["group_id"], feedback_files=None
            )
            _params, _path, request_type, _content_type = _submit_request.call_args[0]
            assert request_type == ("PUT" if kwargs["overwrite"] else "POST")

    @given(
        kwargs=strategies_from_signature(Markus.upload_feedback_file), filename=st.from_regex(r"\w+", fullmatch=True)
    )
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_json_response", return_value=[DUMMY_RETURNS["_decode_json_response"]])
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_upload_feedback_file_bad_title(self, _get_path, _decode_json_response, _submit_request, kwargs, filename):
        with pytest.raises(ValueError):
            dummy_markus().upload_feedback_file(**{**kwargs, "title": filename, "mime_type": None})

    @given(kwargs=strategies_from_signature(Markus.upload_test_group_results))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_upload_test_group_results(self, _get_path, _submit_request, kwargs):
        dummy_markus().upload_test_group_results(**kwargs)
        params = {"test_run_id": kwargs["test_run_id"], "test_output": kwargs["test_output"]}
        _get_path.assert_called_with(
            assignments=kwargs["assignment_id"], groups=kwargs["group_id"], test_group_results=None
        )
        _submit_request.assert_called_with(params, _get_path.return_value, "POST")

    @given(kwargs=strategies_from_signature(Markus.upload_annotations))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_upload_annotations(self, _get_path, _submit_request, kwargs):
        dummy_markus().upload_annotations(**kwargs)
        params = {"annotations": kwargs["annotations"], "force_complete": kwargs["force_complete"]}
        _get_path.assert_called_with(
            assignments=kwargs["assignment_id"], groups=kwargs["group_id"], add_annotations=None
        )
        _submit_request.assert_called_with(params, _get_path.return_value, "POST", "application/json")

    @given(kwargs=strategies_from_signature(Markus.get_annotations))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_json_response")
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_get_annotations(self, _get_path, _decode_json_response, _submit_request, kwargs):
        dummy_markus().get_annotations(**kwargs)
        _get_path.assert_called_with(assignments=kwargs["assignment_id"], groups=kwargs["group_id"], annotations=None)
        _submit_request.assert_called_with(None, f"{_get_path.return_value}.json", "GET")
        _decode_json_response.assert_called_with(_submit_request.return_value)

    @given(kwargs=strategies_from_signature(Markus.update_marks_single_group))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_update_marks_single_group(self, _get_path, _submit_request, kwargs):
        dummy_markus().update_marks_single_group(**kwargs)
        _get_path.assert_called_with(assignments=kwargs["assignment_id"], groups=kwargs["group_id"], update_marks=None)
        _submit_request.assert_called_with(kwargs["criteria_mark_map"], _get_path.return_value, "PUT")

    @given(
        kwargs=strategies_from_signature(Markus.upload_folder_to_repo),
        foldername=st.from_regex(fr"([a-z]+/?)+", fullmatch=True),
    )
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_json_response", return_value=[DUMMY_RETURNS["_decode_json_response"]])
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_upload_folder_to_repo(self, _get_path, _decode_json_response, _submit_request, kwargs, foldername):
        dummy_markus().upload_folder_to_repo(**{**kwargs, "folder_path": foldername})
        _get_path.assert_called_with(
            assignments=kwargs["assignment_id"], groups=kwargs["group_id"], submission_files=None, create_folders=None
        )
        params, path, request_type = _submit_request.call_args[0]
        assert path == _get_path.return_value
        assert params.keys() == {"folder_path"}

    @given(kwargs=strategies_from_signature(Markus.create_extra_marks))
    @patch.object(Markus, '_submit_request', return_value=DUMMY_RETURNS['_submit_request'])
    @patch.object(Markus, '_get_path', return_value=DUMMY_RETURNS['path'])
    def test_create_extra_marks(self, _get_path, _submit_request, kwargs):
        dummy_markus().create_extra_marks(**kwargs)
        params = {
            'extra_marks': kwargs['extra_marks'],
            'description': kwargs['description']
        }
        _get_path.assert_called_with(assignments=kwargs['assignment_id'], groups=kwargs['group_id'],
                                    create_extra_marks=None)
        _submit_request.assert_called_with(params, _get_path.return_value, 'POST')

    @given(kwargs=strategies_from_signature(Markus.remove_extra_marks))
    @patch.object(Markus, '_submit_request', return_value=DUMMY_RETURNS['_submit_request'])
    @patch.object(Markus, '_get_path', return_value=DUMMY_RETURNS['path'])
    def test_remove_extra_marks(self, _get_path, _submit_request, kwargs):
        dummy_markus().remove_extra_marks(**kwargs)
        params = {
            'extra_marks': kwargs['extra_marks'],
            'description': kwargs['description']
        }
        _get_path.assert_called_with(assignments=kwargs['assignment_id'], groups=kwargs['group_id'],
                                    remove_extra_marks=None)
        _submit_request.assert_called_with(params, _get_path.return_value, 'DELETE')

    @given(kwargs=strategies_from_signature(Markus.upload_file_to_repo), filename=file_name_strategy())
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_json_response", return_value=[DUMMY_RETURNS["_decode_json_response"]])
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_upload_file_to_repo(self, _get_path, _decode_json_response, _submit_request, kwargs, filename):
        dummy_markus().upload_file_to_repo(**{**kwargs, "file_path": filename})
        _get_path.assert_called_with(
            assignments=kwargs["assignment_id"], groups=kwargs["group_id"], submission_files=None
        )
        params, path, request_type, _content_type = _submit_request.call_args[0]
        assert path == _get_path.return_value
        assert params.keys() == {"filename", "file_content", "mime_type"}

    @given(kwargs=strategies_from_signature(Markus.remove_file_from_repo), filename=file_name_strategy())
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_json_response", return_value=[DUMMY_RETURNS["_decode_json_response"]])
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_remove_file_from_repo(self, _get_path, _decode_json_response, _submit_request, kwargs, filename):
        dummy_markus().remove_file_from_repo(**{**kwargs, "file_path": filename})
        _get_path.assert_called_with(
            assignments=kwargs["assignment_id"], groups=kwargs["group_id"], submission_files=None, remove_file=None
        )
        params, path, request_type = _submit_request.call_args[0]
        assert path == _get_path.return_value
        assert params.keys() == {"filename"}

    @given(kwargs=strategies_from_signature(Markus.remove_folder_from_repo), foldername=st.from_regex(fr"([a-z]+/?)+"))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_json_response", return_value=[DUMMY_RETURNS["_decode_json_response"]])
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_remove_folder_from_repo(self, _get_path, _decode_json_response, _submit_request, kwargs, foldername):
        dummy_markus().remove_folder_from_repo(**{**kwargs, "folder_path": foldername})
        _get_path.assert_called_with(
            assignments=kwargs["assignment_id"], groups=kwargs["group_id"], submission_files=None, remove_folder=None
        )
        params, path, request_type = _submit_request.call_args[0]
        assert path == _get_path.return_value
        assert params.keys() == {"folder_path"}

    @given(kwargs=strategies_from_signature(Markus.get_files_from_repo))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_get_files_from_repo(self, _get_path, _submit_request, kwargs):
        dummy_markus().get_files_from_repo(**{**kwargs})
        _get_path.assert_called_with(
            assignments=kwargs["assignment_id"], groups=kwargs["group_id"], submission_files=None
        )
        params, path, request_type = _submit_request.call_args[0]
        assert path == _get_path.return_value + ".json"
        if kwargs.get("filename"):
            assert "filename" in params.keys()
        if kwargs.get("collected"):
            assert "collected" in params.keys()

    @given(kwargs=strategies_from_signature(Markus.get_test_specs))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_decode_json_response")
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_get_test_specs(self, _get_path, _decode_json_response, _submit_request, kwargs):
        dummy_markus().get_test_specs(**kwargs)
        _get_path.assert_called_with(assignments=kwargs["assignment_id"], test_specs=None)
        _submit_request.assert_called_with(None, f"{_get_path.return_value}.json", "GET")
        _decode_json_response.assert_called_with(_submit_request.return_value)

    @given(kwargs=strategies_from_signature(Markus.update_test_specs))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_update_test_specs(self, _get_path, _submit_request, kwargs):
        dummy_markus().update_test_specs(**{**kwargs})
        _get_path.assert_called_with(assignments=kwargs["assignment_id"], update_test_specs=None)
        specs = {"specs": kwargs["specs"]}
        _submit_request.assert_called_with(
            specs, f"{_get_path.return_value}.json", "POST", content_type="application/json"
        )

    @given(kwargs=strategies_from_signature(Markus.get_test_files))
    @patch.object(Markus, "_submit_request", return_value=DUMMY_RETURNS["_submit_request"])
    @patch.object(Markus, "_get_path", return_value=DUMMY_RETURNS["path"])
    def test_get_test_files(self, _get_path, _submit_request, kwargs):
        dummy_markus().get_test_files(**kwargs)
        _get_path.assert_called_with(assignments=kwargs["assignment_id"], test_files=None)
        _submit_request.assert_called_with(None, f"{_get_path.return_value}.json", "GET")


class TestMarkusAPIHelpers:
    @given(
        kwargs=strategies_from_signature(Markus._submit_request),
        content_type=st.sampled_from(["application/x-www-form-urlencoded", "application/json"]),
    )
    @patch.object(Markus, "_do_submit_request")
    def test_submit_request_check_types(self, do_submit_request, kwargs, content_type):
        dummy_markus()._submit_request(**{**kwargs, "content_type": content_type})
        params, _path, _request_type, headers = do_submit_request.call_args[0]
        assert isinstance(params, (str, type(None)))
        assert isinstance(headers, dict)

    @given(
        kwargs=strategies_from_signature(Markus._submit_request),
        content_type=st.sampled_from(["multipart/form-data", "bad/content/type"]),
    )
    @patch.object(Markus, "_do_submit_request")
    def test_submit_request_check_catches_invalid(self, do_submit_request, kwargs, content_type):
        try:
            dummy_markus()._submit_request(**{**kwargs, "content_type": content_type})
        except ValueError:
            return
        params, _path, _request_type, headers = do_submit_request.call_args[0]
        assert isinstance(params, (str, type(None)))

    @given(kwargs=strategies_from_signature(Markus._do_submit_request))
    @patch.object(http.client.HTTPConnection, "request")
    @patch.object(http.client.HTTPConnection, "getresponse")
    @patch.object(http.client.HTTPConnection, "close")
    def test__do_submit_request_http(self, request, getresponse, close, kwargs):
        dummy_markus("http")._do_submit_request(**kwargs)
        request.assert_called_once()
        getresponse.assert_called_once()
        close.assert_called_once()

    @given(kwargs=strategies_from_signature(Markus._do_submit_request))
    @patch.object(http.client.HTTPSConnection, "request")
    @patch.object(http.client.HTTPSConnection, "getresponse")
    @patch.object(http.client.HTTPSConnection, "close")
    def test__do_submit_request_https(self, request, getresponse, close, kwargs):
        dummy_markus("https")._do_submit_request(**kwargs)
        request.assert_called_once()
        getresponse.assert_called_once()
        close.assert_called_once()

    @given(kwargs=st.dictionaries(st.text(), st.text()))
    def test_get_path(self, kwargs):
        path = Markus._get_path(**kwargs)
        for k, v in kwargs.items():
            assert k + (f"/{v}" if v is not None else "") in path

    @given(strategies_from_signature(Markus._decode_text_response))
    def test_decode_text_response(self, **kwargs):
        result = Markus._decode_text_response(**kwargs)
        assert isinstance(result, str)

    @given(in_dict=st.dictionaries(st.text(), st.text()))
    def test_decode_text_response(self, in_dict):
        res = json.dumps(in_dict).encode()
        result = Markus._decode_text_response((200, "", res))
        assert isinstance(result, str)
