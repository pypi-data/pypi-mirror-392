# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from aliyunsdkcore.request import RpcRequest

class CreateWorkspaceRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'quickbi-public', '2022-01-01', 'CreateWorkspace','2.2.0')
		self.set_protocol_type('https')
		self.set_method('POST')

	def get_AllowViewAll(self): # Boolean
		return self.get_query_params().get('AllowViewAll')

	def set_AllowViewAll(self, AllowViewAll):  # Boolean
		self.add_query_param('AllowViewAll', AllowViewAll)
	def get_WorkspaceName(self): # String
		return self.get_query_params().get('WorkspaceName')

	def set_WorkspaceName(self, WorkspaceName):  # String
		self.add_query_param('WorkspaceName', WorkspaceName)
	def get_WorkspaceDescription(self): # String
		return self.get_query_params().get('WorkspaceDescription')

	def set_WorkspaceDescription(self, WorkspaceDescription):  # String
		self.add_query_param('WorkspaceDescription', WorkspaceDescription)
	def get_OnlyAdminCreateDatasource(self): # Boolean
		return self.get_query_params().get('OnlyAdminCreateDatasource')

	def set_OnlyAdminCreateDatasource(self, OnlyAdminCreateDatasource):  # Boolean
		self.add_query_param('OnlyAdminCreateDatasource', OnlyAdminCreateDatasource)
	def get_AllowShare(self): # Boolean
		return self.get_query_params().get('AllowShare')

	def set_AllowShare(self, AllowShare):  # Boolean
		self.add_query_param('AllowShare', AllowShare)
	def get_DefaultShareToAll(self): # Boolean
		return self.get_query_params().get('DefaultShareToAll')

	def set_DefaultShareToAll(self, DefaultShareToAll):  # Boolean
		self.add_query_param('DefaultShareToAll', DefaultShareToAll)
	def get_AllowPublish(self): # Boolean
		return self.get_query_params().get('AllowPublish')

	def set_AllowPublish(self, AllowPublish):  # Boolean
		self.add_query_param('AllowPublish', AllowPublish)
	def get_UseComment(self): # Boolean
		return self.get_query_params().get('UseComment')

	def set_UseComment(self, UseComment):  # Boolean
		self.add_query_param('UseComment', UseComment)
