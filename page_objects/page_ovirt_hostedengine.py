import os
import time
import simplejson
import urllib2
from seleniumlib import SeleniumTest
from utils.htmlparser import MyHTMLParser
from utils.machine import Machine
from utils.rhvmapi import RhevmAction


class OvirtHostedEnginePage(SeleniumTest):
    """
    :avocado: disable
    """

    OVIRT_HOSTEDENGINE_FRAME_NAME = "/ovirt-dashboard"
    HOSTEDENGINE_LINK = "XPATH{}//a[@href='#/he']"

    # Start button
    HE_START = "XPATH{}//span[@class='deployment-option-panel-container']/button[text()='Start']"

    # Guide Links
    GETTING_START_LINK = "XPATH{}//a[contains(text(), 'Installation Guide')]"
    MORE_INFORMATION_LINK = "XPATH{}//a[contains(text(), 'oVirt Homepage')]"

    # VM STAGE
    _TITLE = "XPATH{}//input[@title='%s']"
    _PLACEHOLDER = "XPATH{}//input[@placeholder='%s']"
    VM_FQDN = _PLACEHOLDER % 'ovirt-engine.example.com'
    MAC_ADDRESS = _TITLE % 'Enter the MAC address for the VM.'
    ROOT_PASS = "XPATH{}//label[text()='Root Password']//parent::*//input[@type='password']"
    VM_ADVANCED = "XPATH{}//a[text()='Advanced']"

    # TODO
    _DROPDOWN_MENU = "XPATH{}//label[text()='%s']//parent::*//button[contains(@class, 'dropdown-toggle')]"
    NETWORK_DROPDOWN = _DROPDOWN_MENU % 'Network Configuration'
    # TODO
    # BRIDGE_DROPDOWN
    SSH_ACCESS_DROPDOWN = _DROPDOWN_MENU % 'Root SSH Access'
    _DROPDOWN_VALUE = "XPATH{}//ul[@class='dropdown-menu']/li[@value='%s']"
    NETWORK_DHCP = _DROPDOWN_VALUE % 'dhcp'

    NETWORK_STATIC = _DROPDOWN_VALUE % 'static'
    VM_IP = _PLACEHOLDER % '192.168.1.2'
    IP_PREFIX = _PLACEHOLDER % '24'
    DNS_SERVER = "XPATH{}//div[contains(@class, 'multi-row-text-box-input')]" \
        "/input[@type='text']"

    # ENGINE STAGE
    ADMIN_PASS = "XPATH{}//label[text()='Admin Portal Password']//parent::*//input[@type='password']"
    NEXT_BUTTON = "XPATH{}//button[text()='Next']"
    BACK_BUTTON = "XPATH{}//button[text()='Back']"
    CANCEL_BUTTON = "XPATH{}//button[text()='Cancel']"

    # PREPARE VM
    PREPARE_VM_BUTTON = "XPATH{}//button[text()='Prepare VM']"
    REDEPLOY_BUTTON = "XPATH{}//button[text()='Redeploy']"
    PREPARE_VM_SUCCESS_TEXT = "XPATH{}//h3[contains(text(), 'successfully')]"

    # STORAGE STAGE
    # NFS
    _STORAGE_TYPE = "XPATH{}//ul[@class='dropdown-menu']/li[@value='%s']"
    STORAGE_BUTTON = _DROPDOWN_MENU % 'Storage Type'
    STORAGE_NFS = _STORAGE_TYPE % 'nfs'
    STORAGE_CONN = _PLACEHOLDER % 'host:/path'
    MNT_OPT = "XPATH{}//label[text()='Mount Options']//parent::*//input[@type='text']"
    STORAGE_ADVANCED = "XPATH{}//form/div[@class='form-group']/child::*//a[text()='Advanced']"
    NFS_VER_DROPDOWN = _DROPDOWN_MENU % 'NFS Version'
    NFS_AUTO = _DROPDOWN_VALUE % 'auto'
    NFS_V3 = _DROPDOWN_VALUE % 'v3'
    NFS_V4 = _DROPDOWN_VALUE % 'v4'
    NFS_V41 = _DROPDOWN_VALUE % 'v4_1'

    # NFS_V42

    # ISCSI
    _TEXT_LABEL = "XPATH{}//label[text()='%s']//parent::*//input[@type='text']"
    _PASSWORD_LABEL = "XPATH{}//label[text()='%s']//parent::*//input[@type='password']"
    STORAGE_ISCSI = _STORAGE_TYPE % 'iscsi'
    PORTAL_IP_ADDR = _TEXT_LABEL % 'Portal IP Address'
    PORTAL_USER = _TEXT_LABEL % 'Portal Username'
    PORTAL_PASS = _PASSWORD_LABEL % 'Portal Password'
    DISCOVERY_USER = _TEXT_LABEL % 'Discovery Username'
    DISCOVERY_PASS = _PASSWORD_LABEL % 'Discovery Password'

    RETRIEVE_TARGET = "XPATH{}//button[text()='Retrieve Target List']"
    SELECTED_TARGET = "XPATH{}//input[@type='radio'][@name='target']"
    SELECTED_ISCSI_LUN = "XPATH{}//input[@type='radio'][@name='lun']"

    # FC
    STORAGE_FC = _STORAGE_TYPE % 'fc'
    SELECTED_FC_LUN = "XPATH{}//input[@type='radio'][@value='36005076300810b3e0000000000000027']"
    FC_DISCOVER = "XPATH{}//button[@text()='Discover']"

    # GLUSTERFS
    STORAGE_GLUSTERFS = _STORAGE_TYPE % 'glusterfs'

    # FINISH STAGE
    FINISH_DEPLOYMENT = "XPATH{}//button[text()='Finish Deployment']"
    CLOSE_BUTTON = "XPATH{}//button[text()='Close']"

    # CHECKPOINTS
    MAINTENANCE_HINT = "XPATH{}//div[contains(text(), 'Local maintenance')]"
    GLOBAL_HINT = "XPATH{}//div[contains(text(), 'global maintenance')]"
    ENGINE_UP_ICON = "XPATH{}//span[contains(@class, 'pficon-ok')]"

    _MAINTENANCE = "XPATH{}//button[contains(text(), '%s')]"
    LOCAL_MAINTENANCE = _MAINTENANCE % 'local'
    REMOVE_MAINTENANCE = _MAINTENANCE % 'Remove'
    GLOBAL_MAINTENANCE = _MAINTENANCE % 'global'

    LOCAL_MAINTEN_STAT = "XPATH{}//div[contains(text(), 'Agent')]"
    VM_STATUS = "XPATH{}//div[contains(text(), 'State')]"
    HE_RUNNING = "XPATH{}//p[contains(text(),'Hosted Engine is running on')]"

    FAILED_TEXT = "XPATH{}//div[text()='Deployment failed']"

    def get_latest_rhvm_appliance(self, appliance_path):
        """
        Purpose:
            Get the latest rhvm appliance from appliance parent path
        """
        req = urllib2.Request(appliance_path)
        rhvm_appliance_html = urllib2.urlopen(req).read()

        mp = MyHTMLParser()
        mp.feed(rhvm_appliance_html)
        mp.close()
        mp.a_texts.sort()

        rhvm42_link_list = []
        all_link = mp.a_texts
        for link in all_link:
            if "4.2" in link:
                rhvm42_link_list.append(link)

        latest_rhvm_appliance_name = rhvm42_link_list[-1]
        latest_rhvm_appliance = appliance_path + latest_rhvm_appliance_name
        return latest_rhvm_appliance

    def install_rhvm_appliance(self, appliance_path):
        rhvm_appliance_link = self.get_latest_rhvm_appliance(appliance_path)
        local_rhvm_appliance = "/root/%s" % rhvm_appliance_link.split('/')[-1]
        output = self.host.execute("curl -o %s %s" % (local_rhvm_appliance,
                                                      rhvm_appliance_link), timeout=200)
        if output[0] == "False":
            raise Exception(
                "ERR: Failed to download the latest rhvm appliance")

        self.host.execute("rpm -ivh %s --force" % local_rhvm_appliance)
        self.host.execute("rm -rf %s" % local_rhvm_appliance)

    def add_to_etc_host(self):
        pass

    def clean_nfs_storage(self, nfs_ip, nfs_pass, nfs_path):
        host_ins = Machine(
            host_string=nfs_ip, host_user='root', host_passwd=nfs_pass)
        host_ins.execute("rm -rf %s/*" % nfs_path)

    def move_failed_setup_log(self):
        cmd = "find /var/log -type f |grep ovirt-hosted-engine-setup-.*.log"
        ret = self.host.execute(cmd)
        if ret[0] == True:
            if os.path.exists("/var/old_failed_setup_log") == False:
                self.host.execute("mkdir -p /var/old_failed_setup_log")
            self.host.execute("mv /var/log/ovirt-hosted-engine-setup/*.log \
                         /var/old_failed_setup_log/")
        else:
            pass

    def wait_host_status(self, rhvm_ins, host_name, expect_status):
        i = 0
        host_status = "unknown"
        while True:
            if i > 50:
                raise RuntimeError(
                    "Timeout waitting for host %s as current host status is: %s"
                    % (expect_status, host_status))
            host_status = rhvm_ins.list_host("name", host_name)['status']
            if host_status == expect_status:
                break
            elif host_status == 'install_failed':
                raise RuntimeError("Host is not %s as current status is: %s" %
                                   (expect_status, host_status))
            elif host_status == 'non_operational':
                raise RuntimeError("Host is not %s as current status is: %s" %
                                   (expect_status, host_status))
            time.sleep(10)
            i += 1

    def open_page(self):
        self.switch_to_frame(self.OVIRT_HOSTEDENGINE_FRAME_NAME)
        self.click(self.HOSTEDENGINE_LINK)

    def check_no_password_saved(self, root_pass, admin_pass):
        ret_log = self.host.execute(
            "find /var/log -type f |grep ovirt-hosted-engine-setup-ansible-bootstrap_local_vm.*.log"
        )
        appliance_str = "'APPLIANCE_PASSWORD': '%s'" % root_pass
        appliance_cmd = "grep '%s' %s" % (appliance_str, ret_log[1])

        admin_str = "'ADMIN_PASSWORD': '%s'" % admin_pass
        admin_cmd = "grep '%s' %s" % (admin_str, ret_log[1])

        output_appliance_pass = self.host.execute(appliance_cmd)
        output_admin_pass = self.host.execute(admin_cmd)

        if output_appliance_pass[1] or output_admin_pass[1]:
            self.fail()

    def check_no_large_messages(self):
        size1 = self.host.execute(
            "ls -lnt /var/log/messages | awk '{print $5}'")
        time.sleep(10)
        size2 = self.host.execute(
            "ls -lnt /var/log/messages | awk '{print $5}'")
        if int(size2[1]) - int(size1[1]) > 500:
            self.fail()

    def add_additional_host_to_cluster(self, host_ip, host_name, host_pass,
                                       rhvm_fqdn, engine_pass):
        rhvm = RhevmAction(rhvm_fqdn, "admin", engine_pass)
        rhvm.add_host(host_ip, host_name, host_pass, "Default", True)
        if self.wait_host_status(rhvm, host_name, 'up'):
            self.fail()

    def put_host_to_local_maintenance(self):
        self.click(self.LOCAL_MAINTENANCE)
        time.sleep(240)

    def remove_host_from_maintenance(self):
        self.click(self.REMOVE_MAINTENANCE)
        time.sleep(30)

    def put_cluster_to_global_maintenance(self):
        self.click(self.GLOBAL_MAINTENANCE)

    def clean_hostengine_env(self):
        project_path = os.path.dirname(os.path.dirname(__file__))
        clean_he_file = ''.join(
            project_path
        ) + '/test_suites/test_ovirt_hostedengine.py.data/clean_he_env.py'
        self.host.put_file(clean_he_file, '/root/clean_he_env.py')
        self.host.execute("python /root/clean_he_env.py")

    def check_additional_host_socre(self, ip, passwd):
        cmd = "hosted-engine --vm-status --json"
        host_ins = Machine(
            host_string=ip, host_user='root', host_passwd=passwd)
        i = 0
        while True:
            if i > 10:
                raise RuntimeError(
                    "Timeout waitting for host to available running HE.")
            ret = host_ins.execute(cmd)
            true, false = True, False
            if eval(ret[1])["2"]["score"] == 3400:
                break
            time.sleep(10)
            i += 1