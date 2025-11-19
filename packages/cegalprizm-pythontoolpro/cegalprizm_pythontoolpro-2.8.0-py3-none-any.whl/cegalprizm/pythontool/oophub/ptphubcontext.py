# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import os
from cegalprizm.hub import ConnectionParameters, ConnectorFilter, HubClient, BaseContext


class PtpHubContext(object):
    
    __connection_parameters: "ConnectionParameters" = None
    __connector_filter: "ConnectorFilter"
    __hub_channel: "HubClient" = None

    def __init__(self, hub_context: "BaseContext" = None):
        cp = ConnectionParameters()
        if hub_context is not None:
            cp = hub_context.connection_parameters
            self.__connector_filter = hub_context.connector_filter
        else:
            self.__connector_filter = ConnectorFilter()
        if (os.environ.get("PTP_USE_KEYSTONE") == "0"):
            self.__connection_parameters = cp
        else:
            self.__connection_parameters = ConnectionParameters(host=cp.host, port=cp.port, use_tls=cp.use_tls, use_auth=True)

    @property
    def channel(self) -> "HubClient":
        if self.__hub_channel is None:
            # Do not try to get the user token as Hub will handle this
            self.__hub_channel = HubClient(connection_parameters=self.__connection_parameters)
        return self.__hub_channel

    @property
    def connector_filter(self) -> "ConnectorFilter":
        return self.__connector_filter

    def _set_connector_filter(self, connector_filter: "ConnectorFilter"):
        self.__connector_filter = connector_filter

    def force_new(self):
        self.__hub_channel = None

    def close(self):
        if self.__hub_channel is None:
            return
        self.__hub_channel.close()
