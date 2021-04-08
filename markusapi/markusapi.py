# Interface for python to interact with MarkUs API.
#
# The purpose of this Python module is for users to be able to
# perform MarkUs API functions without having to
# specify the API auth key and URL with each call.
#
# DISCLAIMER
#
# This script is made available under the OSI-approved
# MIT license. See http://www.markusproject.org/#license for
# more information. WARNING: This script is still considered
# experimental.
#
# (c) by the authors, 2008 - 2020.
#

import json
import mimetypes
import requests
from typing import Optional, List, Union, Dict
from datetime import datetime
from .response_parser import parse_response


class Markus:
    """A class for interfacing with the MarkUs API."""

    def __init__(self, api_key: str, url: str) -> None:
        """
        Initialize an instance of the Markus class.

        A valid API key can be found on the dashboard page of the GUI,
        when logged in as an admin.

        Keyword arguments:
        api_key  -- any admin API key for the MarkUs instance.
        url      -- the root domain of the MarkUs instance.
        """
        self.api_key = api_key
        self.url = url

    @property
    def _auth_header(self):
        return {"Authorization": f"MarkUsAuth {self.api_key}"}

    def _url(self, tail=""):
        return f"{self.url}/api/{tail}.json"

    @parse_response("json")
    def get_all_users(self) -> requests.Response:
        """
        Return a list of every user in the MarkUs instance.
        Each user is a dictionary object, with the following keys:
        'id', 'user_name', 'first_name', 'last_name',
        'type', 'grace_credits', 'notes_count', 'hidden'.
        """
        return requests.get(self._url("users"), headers=self._auth_header)

    @parse_response("json")
    def new_user(
        self,
        user_name: str,
        user_type: str,
        first_name: str,
        last_name: str,
        section_name: Optional[str] = None,
        grace_credits: Optional[str] = None,
    ) -> requests.Response:
        """
        Add a new user to the MarkUs database.
        Returns a list containing the response's status,
        reason, and data.
        """
        params = {"user_name": user_name, "type": user_type, "first_name": first_name, "last_name": last_name}
        if section_name is not None:
            params["section_name"] = section_name
        if grace_credits is not None:
            params["grace_credits"] = grace_credits
        return requests.post(self._url("users"), params=params, headers=self._auth_header)

    @parse_response("json")
    def get_assignments(self) -> requests.Response:
        """
        Return a list of all assignments.
        """
        return requests.get(self._url("assignments"), headers=self._auth_header)

    @parse_response("json")
    def get_groups(self, assignment_id: int) -> requests.Response:
        """
        Return a list of all groups associated with the given assignment.
        """
        return requests.get(self._url(f"assignments/{assignment_id}/groups"), headers=self._auth_header)

    @parse_response("json")
    def get_groups_by_name(self, assignment_id: int) -> requests.Response:
        """
        Return a dictionary mapping group names to group ids.
        """
        return requests.get(
            self._url(f"assignments/{assignment_id}/groups/group_ids_by_name"), headers=self._auth_header
        )

    @parse_response("json")
    def get_group(self, assignment_id: int, group_id: int) -> requests.Response:
        """
        Return the group info associated with the given id and assignment.
        """
        return requests.get(self._url(f"assignments/{assignment_id}/groups/{group_id}"), headers=self._auth_header)

    @parse_response("json")
    def get_feedback_files(self, assignment_id: int, group_id: int) -> requests.Response:
        """
        Get the feedback files info associated with the assignment and group.
        """
        return requests.get(
            self._url(f"assignments/{assignment_id}/groups/{group_id}/feedback_files"), headers=self._auth_header
        )

    @parse_response("content")
    def get_feedback_file(self, assignment_id: int, group_id: int, feedback_file_id: int) -> requests.Response:
        """
        Get the feedback file associated with the given id, assignment and group.
        WARNING: This will fail for non-text feedback files
        """
        return requests.get(
            self._url(f"assignments/{assignment_id}/groups/{group_id}/feedback_files/{feedback_file_id}"),
            headers=self._auth_header,
        )

    @parse_response("text")
    def get_grades_summary(self, assignment_id: int) -> requests.Response:
        """
        Get grades summary csv file as a string.
        """
        return requests.get(self._url(f"assignments/{assignment_id}/grades_summary"), headers=self._auth_header)

    @parse_response("json")
    def new_marks_spreadsheet(
        self,
        short_identifier: str,
        description: str = "",
        date: Optional[datetime] = None,
        is_hidden: bool = True,
        show_total: bool = True,
        grade_entry_items: Optional[List[Dict[str, Union[str, bool, float]]]] = None,
    ) -> requests.Response:
        """
        Create a new marks spreadsheet
        """
        params = {
            "short_identifier": short_identifier,
            "description": description,
            "date": date,
            "is_hidden": is_hidden,
            "show_total": show_total,
            "grade_entry_items": grade_entry_items,
        }
        return requests.post(self._url("grade_entry_forms"), params=params, headers=self._auth_header)

    @parse_response("json")
    def update_marks_spreadsheet(
        self,
        spreadsheet_id: int,
        short_identifier: Optional[str] = None,
        description: Optional[str] = None,
        date: Optional[datetime] = None,
        is_hidden: Optional[bool] = None,
        show_total: Optional[bool] = None,
        grade_entry_items: Optional[List[Dict[str, Union[str, bool, float]]]] = None,
    ) -> requests.Response:
        """
        Update an existing marks spreadsheet
        """
        params = {
            "short_identifier": short_identifier,
            "description": description,
            "date": date,
            "is_hidden": is_hidden,
            "show_total": show_total,
            "grade_entry_items": grade_entry_items,
        }
        for name in list(params):
            if params[name] is None:
                params.pop(name)
        return requests.put(self._url(f"grade_entry_forms/{spreadsheet_id}"), params=params, headers=self._auth_header)

    @parse_response("json")
    def update_marks_spreadsheets_grades(
        self, spreadsheet_id: int, user_name: str, grades_per_column: Dict[str, float]
    ) -> requests.Response:
        params = {"user_name": user_name, "grade_entry_items": grades_per_column}
        return requests.put(
            self._url(f"grade_entry_forms/{spreadsheet_id}/update_grades"), json=params, headers=self._auth_header
        )

    @parse_response("json")
    def get_marks_spreadsheets(self) -> requests.Response:
        """
        Get all marks spreadsheets.
        """
        return requests.get(self._url(f"grade_entry_forms"), headers=self._auth_header)

    @parse_response("text")
    def get_marks_spreadsheet(self, spreadsheet_id: int) -> requests.Response:
        """
        Get the marks spreadsheet associated with the given id.
        """
        return requests.get(self._url(f"grade_entry_forms/{spreadsheet_id}"), headers=self._auth_header)

    def _upload_feedback_file_internal(
        self,
        url_content: str,
        files: dict,
        params: dict,
        overwrite: bool = True,
    ) -> requests.Response:
        if params["mime_type"] == None:
            params["mime_type"] = "text/plain"
        if overwrite:
            response = requests.put(self._url(url_content), files=files, params=params, headers=self._auth_header)
            raise Exception(response)
        else:
            response = requests.post(self._url(url_content), files=files, params=params, headers=self._auth_header)
            raise Exception(response.text)
    
    @parse_response("json")
    def upload_feedback_file(
        self,
        assignment_id: int,
        group_id: int,
        title: str,
        contents: Union[str, bytes],
        mime_type: Optional[str] = None,
        overwrite: bool = True,
    ) -> requests.Response:
        """
        Upload a feedback file to Markus.

        Keyword arguments:
        assignment_id -- the assignment's id
        group_id      -- the id of the group to which we are uploading
        title         -- the file name that will be displayed (a file extension is required)
        contents      -- what will be in the file (can be a string or bytes)
        mime_type     -- mime type of title file, if None then the mime type will be guessed based on the file extension
        overwrite     -- whether to overwrite a feedback file with the same name that already exists in Markus
        """
        url_content = f"assignments/{assignment_id}/groups/{group_id}/feedback_files"
        if overwrite:
            feedback_files = self.get_feedback_files(assignment_id, group_id)
            feedback_file_id = next((ff.get("id") for ff in feedback_files if ff.get("filename") == title), None)
            if feedback_file_id is not None:
                url_content += f"/{feedback_file_id}"
            else:
                overwrite = False
        files = {"file_content": (title, contents)}
        params = {"filename": title, "mime_type": mime_type or mimetypes.guess_type(title)[0]}
        return self._upload_feedback_file_internal(url_content, files, params, overwrite)

    @parse_response("json")
    def upload_feedback_file_with_test_run_id(
        self,
        test_run_id: int,
        title: str,
        contents: Union[str, bytes],
        mime_type: Optional[str] = None,
        overwrite: bool = True,
    ) -> requests.Response:
        url_content = f"feedback_files"
        if overwrite:
            pass
        files = {"file_content": (title, contents)}
        params = {"filename": title, "mime_type": mime_type or mimetypes.guess_type(title)[0], "test_run_id": test_run_id}
        return self._upload_feedback_file_internal(url_content, files, params, False)

    @parse_response("json")
    def upload_test_group_results(
        self, assignment_id: int, group_id: int, test_run_id: int, test_output: Union[str, Dict]
    ) -> requests.Response:
        """ Upload test results to Markus """
        if not isinstance(test_output, str):
            test_output = json.dumps(test_output)
        params = {"test_run_id": test_run_id, "test_output": test_output}
        return requests.post(
            self._url(f"assignments/{assignment_id}/groups/{group_id}/test_group_results"),
            json=params,
            headers=self._auth_header,
        )

    @parse_response("json")
    def upload_annotations(
        self, assignment_id: int, group_id: int, annotations: List, force_complete: bool = False
    ) -> requests.Response:
        """
        Each element of annotations must be a dictionary with the following keys:
            - filename
            - annotation_category_name
            - content
            - line_start
            - line_end
            - column_start
            - column_end

        This currently only works for plain-text file submissions.
        """
        params = {"annotations": annotations, "force_complete": force_complete}
        return requests.post(
            self._url(f"assignments/{assignment_id}/groups/{group_id}/add_annotations"),
            json=params,
            headers=self._auth_header,
        )

    @parse_response("json")
    def get_annotations(self, assignment_id: int, group_id: Optional[int] = None) -> requests.Response:
        """
        Return a list of dictionaries containing information for each annotation in the assignment
        with id = assignment_id. If group_id is not None, return only annotations for the given group.
        """
        return requests.get(
            self._url(f"assignments/{assignment_id}/groups/{group_id}/annotations"), headers=self._auth_header
        )

    @parse_response("json")
    def update_marks_single_group(
        self, criteria_mark_map: dict, assignment_id: int, group_id: int
    ) -> requests.Response:
        """
        Update the marks of a single group.
        Only the marks specified in criteria_mark_map will be changed.
        To set a mark to unmarked, use 'nil' as it's value.
        Otherwise, marks must have valid numeric types (floats or ints).
        Criteria are specified by their title. Titles must be formatted
        exactly as they appear in the MarkUs GUI, punctuation included.
        If the criterion is a Rubric, the mark just needs to be the
        rubric level, and will be multiplied by the weight automatically.

        Keyword arguments:
        criteria_mark_map -- maps criteria to the desired grade
        assignment_id     -- the assignment's id
        group_id          -- the id of the group whose marks we are updating
        """
        return requests.put(
            self._url(f"assignments/{assignment_id}/groups/{group_id}/update_marks"),
            json=criteria_mark_map,
            headers=self._auth_header,
        )

    @parse_response("json")
    def update_marking_state(self, assignment_id: int, group_id: int, new_marking_state: str) -> requests.Response:
        """ Update marking state for a single group to either 'complete' or 'incomplete' """
        params = {"marking_state": new_marking_state}
        return requests.put(
            self._url(f"assignments/{assignment_id}/groups/{group_id}/update_marking_state"),
            params=params,
            headers=self._auth_header,
        )

    @parse_response("json")
    def create_extra_marks(
        self, assignment_id: int, group_id: int, extra_marks: float, description: str
    ) -> requests.Response:
        """
        Create new extra mark for the particular group.
        Mark specified in extra_marks will be created
        """
        params = {"extra_marks": extra_marks, "description": description}
        return requests.post(
            self._url(f"assignments/{assignment_id}/groups/{group_id}/create_extra_marks"),
            params=params,
            headers=self._auth_header,
        )

    @parse_response("json")
    def remove_extra_marks(
        self, assignment_id: int, group_id: int, extra_marks: float, description: str
    ) -> requests.Response:
        """
        Remove the extra mark for the particular group.
        Mark specified in extra_marks will be removed
        """
        params = {"extra_marks": extra_marks, "description": description}
        return requests.delete(
            self._url(f"assignments/{assignment_id}/groups/{group_id}/remove_extra_marks"),
            params=params,
            headers=self._auth_header,
        )

    @parse_response("content")
    def get_files_from_repo(
        self, assignment_id: int, group_id: int, filename: Optional[str] = None, collected: bool = True
    ) -> requests.Response:
        """
        Return file content from the submission of a single group. If <filename> is specified,
        return the content of a single file, otherwise return the content of a zipfile containing
        the content of all submission files.

        If <collected> is True, return the collected version of the files, otherwise return the most
        recent version of the files.

        The method returns None if there are no files to collect.
        """
        params = {}
        if collected:
            params["collected"] = collected
        if filename:
            params["filename"] = filename
        return requests.get(
            self._url(f"assignments/{assignment_id}/groups/{group_id}/submission_files"),
            params=params,
            headers=self._auth_header,
        )

    @parse_response("json")
    def upload_folder_to_repo(self, assignment_id: int, group_id: int, folder_path: str) -> requests.Response:
        params = {"folder_path": folder_path}
        return requests.post(
            self._url(f"assignments/{assignment_id}/groups/{group_id}/submission_files/create_folders"),
            params=params,
            headers=self._auth_header,
        )

    @parse_response("json")
    def upload_file_to_repo(
        self,
        assignment_id: int,
        group_id: int,
        file_path: str,
        contents: Union[str, bytes],
        mime_type: Optional[str] = None,
    ) -> requests.Response:
        """
        Upload a file at file_path with content contents to the assignment directory
        in the repo for group with id group_id.

        The file_path should be a relative path from the assignment directory of a repository.
        For example, if you want to upload a file to A1/somesubdir/myfile.txt then the short identifier
        of the assignment with id assignment_id should be A1 and the file_path argument should be:
        'somesubdir/myfile.txt'
        """
        files = {"file_content": (file_path, contents)}
        params = {"filename": file_path, "mime_type": mime_type or mimetypes.guess_type(file_path)[0]}
        return requests.post(
            self._url(f"assignments/{assignment_id}/groups/{group_id}/submission_files"),
            files=files,
            params=params,
            headers=self._auth_header,
        )

    @parse_response("json")
    def remove_file_from_repo(self, assignment_id: int, group_id: int, file_path: str) -> requests.Response:
        """
        Remove a file at file_path from the assignment directory in the repo for group with id group_id.

        The file_path should be a relative path from the assignment directory of a repository.
        For example, if you want to remove a file A1/somesubdir/myfile.txt then the short identifier
        of the assignment with id assignment_id should be A1 and the file_path argument should be:
        'somesubdir/myfile.txt'
        """
        params = {"filename": file_path}
        return requests.delete(
            self._url(f"assignments/{assignment_id}/groups/{group_id}/submission_files/remove_file"),
            params=params,
            headers=self._auth_header,
        )

    @parse_response("json")
    def remove_folder_from_repo(self, assignment_id: int, group_id: int, folder_path: str) -> requests.Response:
        """
        Remove a folder at folder_path and all its contents for group with id grou;_id.

        The file_path should be a relative path from the assignment directory of a repository.
        For example, if you want to remove a folder A1/somesubdir/ then the short identifier
        of the assignment with id assignment_id should be A1 and the folder_path argument should be:
        'somesubdir/'
        """
        params = {"folder_path": folder_path}
        return requests.delete(
            self._url(f"assignments/{assignment_id}/groups/{group_id}/submission_files/remove_folder"),
            params=params,
            headers=self._auth_header,
        )

    @parse_response("json")
    def get_test_specs(self, assignment_id: int) -> requests.Response:
        """
        Get the test spec settings for an assignment with id <assignment_id>.
        """
        return requests.get(self._url(f"assignments/{assignment_id}/test_specs"), headers=self._auth_header)

    @parse_response("json")
    def update_test_specs(self, assignment_id: int, specs: Dict) -> requests.Response:
        """
        Update the test spec settings for an assignment with id <assignment_id> to be <specs>.
        """
        params = {"specs": specs}
        return requests.post(
            self._url(f"assignments/{assignment_id}/update_test_specs"), json=params, headers=self._auth_header
        )

    @parse_response("content")
    def get_test_files(self, assignment_id: int) -> requests.Response:
        """
        Return the content of a zipfile containing the content of all files uploaded for automated testing of
        the assignment with id <assignment_id>.
        """
        return requests.get(self._url(f"assignments/{assignment_id}/test_files"), headers=self._auth_header)

    @parse_response("json")
    def get_starter_file_entries(self, assignment_id: int, starter_file_group_id: int) -> requests.Response:
        """
        Return the name of all entries for a given starter file group. Entries are file or directory names.
        """
        return requests.get(
            self._url(f"assignments/{assignment_id}/starter_file_groups/{starter_file_group_id}/entries"),
            headers=self._auth_header,
        )

    @parse_response("json")
    def create_starter_file(
        self, assignment_id: int, starter_file_group_id: int, file_path: str, contents: Union[str, bytes]
    ) -> requests.Response:
        """
        Upload a starter file to the starter file group with id=<starter_file_group_id> for assignment with
        id=<assignment_id>. The file_path should be a relative path from the starter file group's root directory.
        """
        files = {"file_content": (file_path, contents)}
        params = {"filename": file_path}
        return requests.post(
            self._url(f"assignments/{assignment_id}/starter_file_groups/{starter_file_group_id}/create_file"),
            params=params,
            files=files,
            headers=self._auth_header,
        )

    @parse_response("json")
    def create_starter_folder(
        self, assignment_id: int, starter_file_group_id: int, folder_path: str
    ) -> requests.Response:
        """
        Create a folder for the the starter file group with id=<starter_file_group_id> for assignment with
        id=<assignment_id>. The file_path should be a relative path from the starter file group's root directory.
        """
        params = {"folder_path": folder_path}
        return requests.post(
            self._url(f"assignments/{assignment_id}/starter_file_groups/{starter_file_group_id}/create_folder"),
            params=params,
            headers=self._auth_header,
        )

    @parse_response("json")
    def remove_starter_file(self, assignment_id: int, starter_file_group_id: int, file_path: str) -> requests.Response:
        """
        Remove a starter file from the starter file group with id=<starter_file_group_id> for assignment with
        id=<assignment_id>. The file_path should be a relative path from the starter file group's root directory.
        """
        params = {"filename": file_path}
        return requests.delete(
            self._url(f"assignments/{assignment_id}/starter_file_groups/{starter_file_group_id}/remove_file"),
            params=params,
            headers=self._auth_header,
        )

    @parse_response("json")
    def remove_starter_folder(
        self, assignment_id: int, starter_file_group_id: int, folder_path: str
    ) -> requests.Response:
        """
        Remove a folder from the starter file group with id=<starter_file_group_id> for assignment with
        id=<assignment_id>. The file_path should be a relative path from the starter file group's root directory.
        """
        params = {"folder_path": folder_path}
        return requests.delete(
            self._url(f"assignments/{assignment_id}/starter_file_groups/{starter_file_group_id}/remove_folder"),
            params=params,
            headers=self._auth_header,
        )

    @parse_response("content")
    def download_starter_file_entries(self, assignment_id: int, starter_file_group_id: int) -> requests.Response:
        """
        Return the content of a zipfile containing the content of all starter files from the starter file group with
        id=<starter_file_group_id>.
        """
        return requests.get(
            self._url(f"assignments/{assignment_id}/starter_file_groups/{starter_file_group_id}/download_entries"),
            headers=self._auth_header,
        )

    @parse_response("json")
    def get_starter_file_groups(self, assignment_id: int) -> requests.Response:
        """
        Return all starter file groups for the assignment with id=<assignment_id>
        """
        return requests.get(self._url(f"assignments/{assignment_id}/starter_file_groups"), headers=self._auth_header)

    @parse_response("json")
    def create_starter_file_group(self, assignment_id: int) -> requests.Response:
        """
        Create a starter file groups for the assignment with id=<assignment_id>
        """
        return requests.post(self._url(f"assignments/{assignment_id}/starter_file_groups"), headers=self._auth_header)

    @parse_response("json")
    def get_starter_file_group(self, assignment_id: int, starter_file_group_id: int) -> requests.Response:
        """
        Return the starter file group with id=<starter_file_group_id> for the assignment with id=<assignment_id>
        """
        return requests.get(
            self._url(f"assignments/{assignment_id}/starter_file_groups/{starter_file_group_id}"),
            headers=self._auth_header,
        )

    @parse_response("json")
    def update_starter_file_group(
        self,
        assignment_id: int,
        starter_file_group_id: int,
        name: Optional[str] = None,
        entry_rename: Optional[str] = None,
        use_rename: Optional[bool] = None,
    ) -> requests.Response:
        """
        Update the starter file group with id=<starter_file_group_id> for the assignment with id=<assignment_id>
        """
        params = {}
        if name is not None:
            params["name"] = name
        if entry_rename is not None:
            params["entry_rename"] = entry_rename
        if use_rename is not None:
            params["use_rename"] = use_rename
        return requests.put(
            self._url(f"assignments/{assignment_id}/starter_file_groups/{starter_file_group_id}"),
            params=params,
            headers=self._auth_header,
        )

    @parse_response("json")
    def delete_starter_file_group(self, assignment_id: int, starter_file_group_id: int) -> requests.Response:
        """
        Delete the starter file group with id=<starter_file_group_id> for the assignment with id=<assignment_id>
        """
        return requests.delete(
            self._url(f"assignments/{assignment_id}/starter_file_groups/{starter_file_group_id}"),
            headers=self._auth_header,
        )
