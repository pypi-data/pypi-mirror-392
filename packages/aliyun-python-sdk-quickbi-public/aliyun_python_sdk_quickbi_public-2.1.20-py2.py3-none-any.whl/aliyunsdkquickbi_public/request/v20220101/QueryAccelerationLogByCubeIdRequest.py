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

class QueryAccelerationLogByCubeIdRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'quickbi-public', '2022-01-01', 'QueryAccelerationLogByCubeId','2.2.0')
		self.set_protocol_type('https')
		self.set_method('POST')

	def get_StartDate(self): # String
		return self.get_query_params().get('StartDate')

	def set_StartDate(self, StartDate):  # String
		self.add_query_param('StartDate', StartDate)
	def get_PageSize(self): # Integer
		return self.get_query_params().get('PageSize')

	def set_PageSize(self, PageSize):  # Integer
		self.add_query_param('PageSize', PageSize)
	def get_CubeId(self): # String
		return self.get_query_params().get('CubeId')

	def set_CubeId(self, CubeId):  # String
		self.add_query_param('CubeId', CubeId)
	def get_EndDate(self): # String
		return self.get_query_params().get('EndDate')

	def set_EndDate(self, EndDate):  # String
		self.add_query_param('EndDate', EndDate)
	def get_PageNo(self): # Integer
		return self.get_query_params().get('PageNo')

	def set_PageNo(self, PageNo):  # Integer
		self.add_query_param('PageNo', PageNo)
