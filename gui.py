#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import wx
import wx.adv as wiz
import win32api
import os
import threading
import time

import coolutils
import wis_cd

# http://stackoverflow.com/questions/827371/is-there-a-way-to-list-all-the-available-drive-letters-in-python

drives = win32api.GetLogicalDriveStrings()
drives = drives.split('\000')[:-1]
print(drives)
########################################################################


def wx_expanded(widget, padding=0):
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(widget, 1, wx.EXPAND|wx.ALL, padding)
    return sizer


class TitledPage(wiz.WizardPageSimple):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, title):
        """Constructor"""
        wiz.WizardPageSimple.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = sizer
        self.SetSizer(sizer)

        title = wx.StaticText(self, -1, title)
        title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        sizer.Add(title, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 5)


class Page2(TitledPage):
    def __init__(self, parent):
        TitledPage.__init__(self, parent, 'Select Saab WIS CD')

        self.valid_path = False
        self.directory_dialog = wx.DirDialog(self, 'Select WIS CD directory', '', wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)

        self.sizer.Add(wx.StaticText(self, -1, "\nPlease select the location of the Saab WIS CD drive"))
        wis_browse_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.wis_location_text_ctrl = wx.TextCtrl(self, -1)
        self.wis_location_text_ctrl.Disable()
        wis_browse_sizer.Add(self.wis_location_text_ctrl, 1, wx.EXPAND)

        browse_button = wx.Button(self, -1, "Browse")
        browse_button.Bind(wx.EVT_BUTTON, self.display_dialog)
        wis_browse_sizer.Add(browse_button)

        self.sizer.Add(wis_browse_sizer, 0, wx.EXPAND)

        """
        select_model_language_grid = wx.FlexGridSizer(2, 3, 1, 1)  # TODO
        select_model_language_grid.AddGrowableRow(1)
        #select_model_language_grid.AddGrowableCol(1)
        #select_model_language_grid.SetFlexibleDirection(wx.HORIZONTAL)

        select_model_language_grid.Add(wx.StaticText(self, -1, "\nSelect model(s)"))
        select_model_language_grid.Add(wx.StaticText(self, -1, "\nSelect language(s)"), 0, wx.ALIGN_RIGHT)
        select_model_language_grid.AddStretchSpacer()

        self.select_model_check_list_box = wx.CheckListBox(self)
        self.select_language_check_list_box = wx.CheckListBox(self)
        select_model_language_grid.Add(self.select_model_check_list_box, 1, wx.EXPAND)
        select_model_language_grid.Add(self.select_language_check_list_box, 1, wx.ALIGN_RIGHT|wx.EXPAND)
        select_model_language_grid.AddStretchSpacer()

        self.sizer.Add(select_model_language_grid, 1, wx.EXPAND)
        """

        # Create sizers
        select_model_language_sizer = wx.BoxSizer(wx.HORIZONTAL)
        select_model_sizer = wx.BoxSizer(wx.VERTICAL)
        select_language_sizer = wx.BoxSizer(wx.VERTICAL)

        # Select model
        select_model_sizer.Add(wx.StaticText(self, -1, "\nSelect model(s)"))
        self.model_check_list_box = wx.CheckListBox(self)
        select_model_sizer.Add(self.model_check_list_box, 1)

        # Select language
        select_language_sizer.Add(wx.StaticText(self, -1, "\nSelect language(s)"))
        self.language_check_list_box = wx.CheckListBox(self)
        select_language_sizer.Add(self.language_check_list_box, 1)

        select_model_language_sizer.Add(select_model_sizer, 0, wx.EXPAND)
        select_model_language_sizer.AddStretchSpacer()
        select_model_language_sizer.Add(select_language_sizer, 0, wx.EXPAND)
        self.sizer.Add(select_model_language_sizer, 1, wx.EXPAND)

    def display_dialog(self, event):
        if self.directory_dialog.ShowModal() == wx.ID_OK:
            path = self.directory_dialog.GetPath()
            if wis_cd.SaabWISCD.is_valid_wis_cd(path):
                self.wis_location_text_ctrl.SetValue(path)
                #self.FindWindowById(wx.ID_FORWARD).Enable()

                cd = wis_cd.SaabWISCD(path)

                self.model_check_list_box.Set(cd.get_models())
                self.language_check_list_box.Set(cd.get_languages())
            else:
                wx.MessageBox('Could not recognize the selected directory as a Saab WIS CD',
                              'Error', wx.OK | wx.ICON_EXCLAMATION)

    def on_enter(self):
        self.FindWindowById(wx.ID_FORWARD).Disable()
        #if Page2.is_valid_cd_directory(self.directory_dialog.GetPath()):
        #    self.FindWindowById(wx.ID_FORWARD).Enable()

    def on_exit(self):
        self.FindWindowById(wx.ID_FORWARD).Enable()


class Page3(TitledPage):
    def __init__(self, parent):
        TitledPage.__init__(self, parent, 'CoolUtils CAD ConverterX')

        self.dependency_check_thread = None

        self.sizer.Add(wx.StaticText(self, -1, '\nPlease download and install Total CAD ConverterX from the link below.'
                                               '\n'
                                               '\nThis program will be used to convert the images on the CD to a '
                                               '\nstandard web format. The trial version is sufficient for this task.'
                                               '\n'))

        self.sizer.Add(wx.adv.HyperlinkCtrl(self, -1, 'https://www.coolutils.com/TotalCADConverterX',
                                            url='https://www.coolutils.com/TotalCADConverterX'))

        self.program_detected_text_ctrl = wx.StaticText(self, -1)
        self.sizer.Add(self.program_detected_text_ctrl)

    def check_dependency(self):
        while not coolutils.cad_converterx_is_installed():
            if self and not self.IsShown():
                return
            time.sleep(3)

        self.FindWindowById(wx.ID_FORWARD).Enable()
        self.program_detected_text_ctrl.SetLabelText('\nTotal CAD ConverterX has been detected.')

    def on_enter(self):
        self.FindWindowById(wx.ID_FORWARD).Disable()
        if coolutils.cad_converterx_is_installed():
            self.FindWindowById(wx.ID_FORWARD).Enable()
            self.program_detected_text_ctrl.SetLabelText('\nTotal CAD ConverterX has been detected.')
        else:
            self.program_detected_text_ctrl.SetLabelText('\nUnable to find Total CAD ConverterX, please install it to continue.')
            self.dependency_check_thread = threading.Thread(target=self.check_dependency)
            self.dependency_check_thread.start()

    def on_exit(self):
        self.FindWindowById(wx.ID_FORWARD).Enable()


class SaabWizard(wx.adv.Wizard):
    def __init__(self):
        super(wx.adv.Wizard, self).__init__(None, -1, 'Saab WIS HTML5 installer', bitmap=wx.Bitmap('saab_wizard_logo.png'))
        self.page1 = TitledPage(self, "Welcome")
        self.page2 = Page2(self)
        self.page3 = Page3(self)
        self.page4 = TitledPage(self, "Select model and language")
        self.page5 = TitledPage(self, "Select installation directory")
        self.page6 = TitledPage(self, "Installation is ready to commence")
        self.page7 = TitledPage(self, "Installing")
        self.page8 = TitledPage(self, "Done")

        self.FitToPage(self.page1)
        self.page1.sizer.Add(
            wx.StaticText(self.page1, -1, "\nWelcome to the Saab WIS HTML5 installer.\nThis wizard will guide you"
                                          "through the installation of the system."))

        self.page5.sizer.Add(wx.StaticText(self.page5, -1, "\nThis is the last page."))

        # Set the initial order of the pages
        self.page1.SetNext(self.page2)
        self.page2.SetPrev(self.page1)
        self.page2.SetNext(self.page3)
        self.page3.SetPrev(self.page2)
        self.page3.SetNext(self.page4)
        self.page4.SetPrev(self.page3)
        self.page4.SetNext(self.page5)
        self.page5.SetPrev(self.page4)
        self.page5.SetNext(self.page6)
        #self.page6.SetPrev(self.page5)
        self.page6.SetNext(self.page7)
        self.page7.SetPrev(self.page6)

        self.GetPageAreaSizer().Add(self.page1, flag=wx.ALL|wx.EXPAND)

        # Events
        self.Bind(wiz.EVT_WIZARD_PAGE_CHANGED, self.on_page_changed)
        self.Bind(wiz.EVT_WIZARD_BEFORE_PAGE_CHANGED, self.on_before_page_changed)

    def on_page_changed(self, event):
        p = event.GetPage()

        if hasattr(p, 'on_enter'):
            p.on_enter()

    def on_before_page_changed(self, event):
        p = event.GetPage()

        if hasattr(p, 'on_exit'):
            p.on_exit()

    def run(self):
        self.RunWizard(self.page1)

        self.Destroy()


# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    wizard = SaabWizard()
    wizard.run()
    app.MainLoop()
