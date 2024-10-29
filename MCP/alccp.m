% Simple CCP for ENGG2K3K Bladerunner 2024 Project
% 
% Author: Alan
% Date: 9 September 2024
% Revision History:
%   V1.0: Initial release based on MCP-CCP Protocol Specification Version 2.3
%
% Standard use cases 
%   Start CCP: c = simple_ccp();
%   Connect to MCP: c.connect();
%
% Alternate use cases
%   Start CCP with a particular bladerunner id: c = simple_ccp("bladerunner_id","BR00");
%   Start CCP with a particular bladerunner id and connect to MCP on specified IP/Port: c = simple_ccp("bladerunner_id","BR00","mcp_addr","https://url.au.m.mimecastprotect.com/s/uhklCXLW6DiXnwVwqimt7CW8js3?domain=127.0.0.1","mcp_port",2000);
%   Start CCP with a particular bladerunner id and on specified port: m = simple_ccp("bladerunner_id","BR00","ccp_port",3000);
%

classdef simple_ccp < handle

    properties (Access=protected)
        mcp_addr 
        mcp_port
        br_id
        cli_h
        state 
    end

    methods (Access=public)
        % constructor
        function obj = simple_ccp(varargin)

            % parse inputs
            p = inputParser;
            addOptional(p,'bladerunner_id', "BR00");
            addOptional(p,'mcp_addr', "https://url.au.m.mimecastprotect.com/s/uhklCXLW6DiXnwVwqimt7CW8js3?domain=127.0.0.1");
            addOptional(p,'mcp_port', 2001);
            addOptional(p,'ccp_addr', "https://url.au.m.mimecastprotect.com/s/uhklCXLW6DiXnwVwqimt7CW8js3?domain=127.0.0.1");
            addOptional(p,'ccp_port', 2002);
            parse(p,varargin{:});
            inargs = p.Results;

            % save mcp address/port
            obj.mcp_addr = inargs.mcp_addr;
            obj.mcp_port = inargs.mcp_port;
            obj.br_id = inargs.bladerunner_id;

            % create udp socket
            obj.cli_h = udpport("datagram","LocalHost",inargs.ccp_addr,"LocalPort",inargs.ccp_port);
            configureCallback(obj.cli_h,"datagram",1,@obj.recvFcn)
            obj.state = cstate.STARTED;
        end

        % connect to MCP
        function connect(obj)
            obj.update('connect')
        end
    end

    methods(Access=private)
        % main state machine
        function update(obj,s)
            switch obj.state
                case cstate.STARTED
                    if strcmp(s,'connect')
                        msg = struct("client_type","ccp","message","CCIN", ...
                            "client_id",obj.br_id,"Timestamp",getTimestamp());
                        obj.sendmsg(msg);
                    else
                        error('Cannot run %s() because CCP is in %s state',s,obj.state)
                    end
            end
        end

        % encodes message as JSON and send
        function sendmsg(obj,msg)
            msg = jsonencode(msg);
            write(obj.cli_h,msg,"char",obj.mcp_addr,obj.mcp_port);
        end

        % handles incoming JSON packets
        function recvFcn(obj,src,~)
            m = read(src,1,"char");
            msg = jsondecode(m.Data);

            fprintf(1,'\nMessage received by %s:\n',obj.br_id);
            disp(jsonencode(msg,"PrettyPrint",true))
        end
    end
    
end

%%% helper functions %%%

function ts = getTimestamp()
    ts = datestr(now,'yyyy-mm-ddTHH:MM+10Z'); % hard coded GMT+10, timestamp will probably need seconds 
end
