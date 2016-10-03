import paramiko, os
from paramiko_server import ParamikoServer
from process import SingleCPUProcess


class OSDCProcess(SingleCPUProcess):
    def __init__(self, pid, logfile):
        super(OSDCProcess, self).__init__(logfile)
        self.pid = pid

    def is_running(self):
        raise NotImplementedError("Not implemented yet.")

    def kill(self):
        raise NotImplementedError("Not implemented yet.")

    def clean(self):
        raise NotImplementedError("Not implemented yet.")


class OSDCServer(ParamikoServer):
    def __init__(self, utup, cpus, roots, credentials):
        super(OSDCServer, self).__init__(utup, cpus, roots, credentials)

    def connect(self):
        while True:
            os.system("ssh-agent -s")
            sshAgentList = os.popen("find /tmp/ -type s -name agent.* 2>/dev/null | grep '/tmp/ssh-.*/agent.*'").read().split("\n")[:-1]
            os.environ['SSH_AUTH_SOCK'] = sshAgentList[0]
            retCode = os.system("ssh-add /var/www/jongkaishackleton-www.pem")
            if retCode == 0:
                for i in range(1, len(sshAgentList)):
                    agentPID = int(sshAgentList[i].split(".")[1])+1
                    os.system("kill " + str(agentPID))
                break
            else:
                agentPID = int(sshAgentList[0].split(".")[1])+1
                # TODO: add sleep
                os.system("kill " + str(agentPID))

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # ssh -A jrising@griffin.opensciencedatacloud.org
        client.connect(self.credentials['loginnode'], username=self.credentials['username'])

        # Open up a session
        s = client.get_transport().open_session()
        paramiko.agent.AgentRequestHandler(s)

        s.get_pty()
        s.invoke_shell()

        self.client = client
        self.session = s

        # ssh -A ubuntu@172.17.199.2
        print(s)
        stdout, stderr = self.run_command('ssh -A ubuntu@' + self.credentials['instanceip'])
        print(self, s)
        stdout, stderr = self.run_command('hostname > arrived')

        self.connected = True

