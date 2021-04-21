# coding=utf8
'''
Copyright (R) 2021 Vaibhav.Gilhotra <spaceholder_email>

Published under Apache 2.0 License (http://www.apache.org/licenses/LICENSE-2.0.html).
-------------------------------------------------------------------------------------

This module define all propgrid class and functions used in main_frame.

Some editor dialog use the singleton method to promote efficiency.
'''

import os
import wx.propgrid as wxpg
import AttrsDef
import wx, types, colour
import re
from DEUtils import remove_double_quote, get_colors_in_scheme
from UIClass import ImageSingleChoiceDialog, ArrowTypeDialog, \
                    ColorSingleChoiceDialog, ColorSchemeDialog, \
                    DialogTextEditor
import DEUtils
import tempfile

### Some global var.
CS_DIALOG = None
NS_DIALOG = None
AT_DIALOG = None

def get_root_window(window):
    
    p = window
    while 1:
        r1 = p.GetParent()
        if r1 is None:
            return p
        else:
            p = r1 
            
    return None

class CSDialog(ColorSchemeDialog):
    '''A Dialog to select a colorscheme.'''
    
    @staticmethod
    def get_dialog(parent, scheme='x11'):
        '''A factory method to return singleton.'''
        global CS_DIALOG
        if CS_DIALOG is None:
            CS_DIALOG = CSDialog(parent, scheme)
        
        CS_DIALOG.reset()
        return CS_DIALOG
    
    def __init__(self, parent, scheme='x11'):
        
        ColorSchemeDialog.__init__(self, parent)
        
        self.choice = AttrsDef.E_COLORSCHEME
        
        il = get_root_window(self).image_list['colorscheme']
        self.m_list.AssignImageList(il, 0)
        
        # Change dialog size to fit the image size.        
        w, h = il.GetBitmap(0).GetSize()
        if os.sys.platform in ['win32', 'win64']:
            self.SetSize(int(w*4.5), h*4)
        elif os.sys.platform == 'darwin':
            self.SetSize(int(w*4.5), h*5)
        elif os.sys.platform[:5] == 'linux':
            self.SetSize(int(w*5), h*5.5)
        else:
            self.SetSize(int(w*5), h*5)
            
        self.updateList()
        
        self.m_list.Bind(wx.EVT_LEFT_DCLICK, self.onOK)
    
    def reset(self):
        self.m_searchCtrl.SetValue('')
        self.onSearch(None)
    
    def SetColorScheme(self, scheme):
        s = scheme.strip().lower()
        idx = self.m_list.FindItem(0, s)
        if idx < 0:
            return
        self.m_list.Select(idx, True)
        self.m_list.Focus(idx)
    
    def onSearch(self, event):
        s_text = self.m_searchCtrl.GetValue()
        scheme_list = self.choice
        
        search_result = list(filter(lambda s:s.find(s_text) > -1, scheme_list))
        self.updateList(search_result)
    
    def GetColorScheme(self):
        idx = self.m_list.GetFirstSelected()
        if idx == -1:
            return ''
        else:
            return self.m_list.GetItemText(idx)
    
    def updateList(self, scheme_list=None):
        
        all_scheme = self.choice
        if scheme_list is None:
            scheme_list = all_scheme
        
        self.m_list.ClearAll()
        for x in range(len(scheme_list)):
            c = scheme_list[x]
            img_idx = all_scheme.index(c)
            self.m_list.InsertItem(x, c, img_idx)
            
        return

    def onOK(self, event):
        idx = self.m_list.GetFirstSelected()
        if idx == -1:
            return
        
        self.EndModal(wx.ID_OK)

class CSCDialog(ColorSingleChoiceDialog):
    '''A Dialog to select a color.'''
    
    def __init__(self, parent, scheme='x11'):
        ColorSingleChoiceDialog.__init__(self, parent)
        
        self.SetTitle('Pick a color')
        self.m_staticText_message.SetLabel('Select a color in "%s":'%scheme)
        
        self.choice = get_colors_in_scheme(scheme)
        
        self.updateList()
        
        self.m_list.Bind(wx.EVT_LEFT_DCLICK, self.onOK)
        
    def SetColorString(self, color):
        s = color.strip().lower()
        idx = self.m_list.FindItem(0, s)
        if idx < 0:
            return
        self.m_list.Select(idx, True)
        self.m_list.Focus(idx)
        self.m_list.SetFocus()
    
    def onSearch(self, event):
        s_text = self.m_searchCtrl.GetValue()
        color_list = sorted(self.choice.keys())
        # color_list.sort()
        
        search_result = list(filter(lambda s:s.find(s_text) > -1, color_list))
        self.updateList(search_result)
    
    def GetColorString(self):
        idx = self.m_list.GetFirstSelected()
        if idx == -1:
            return ''
        else:
            return self.m_list.GetItemText(idx)
    
    def updateList(self, color_list=None):
        
        if color_list is None:
            color_list = sorted(self.choice.keys())
            # color_list.sort()
        
        self.m_list.ClearAll()
        self.m_list.InsertColumn(0, 'COLOR NAME')
        w, _ = self.m_list.GetSize()
        self.m_list.SetColumnWidth(0, w*0.92)
        for x in range(len(color_list)):
            c = color_list[x]
            self.m_list.InsertItem(x, c)
            r,g,b = self.choice[c]
            v = max(r,g,b)/255.0
            if v < 0.5:
                self.m_list.SetItemTextColour(x, wx.Colour(255,255,255))
            self.m_list.SetItemBackgroundColour(x, wx.Colour(r,g,b))
            
        return

    def onOK(self, event):
        idx = self.m_list.GetFirstSelected()
        if idx == -1:
            return
        
        self.EndModal(wx.ID_OK)
        

class NodeShapeDialog(ImageSingleChoiceDialog):
    '''A Dialog to select node shape.'''
    
    @staticmethod
    def get_dialog(parent):
        '''A factory method to return singleton.'''
        global NS_DIALOG
        if NS_DIALOG is None:
            NS_DIALOG = NodeShapeDialog(parent)
        
        return NS_DIALOG
    
    def __init__(self, parent):
        
        ImageSingleChoiceDialog.__init__(self, parent)
        
        self.SetTitle('Select node shape')
        self.m_message.SetLabel('Choice a node shape below:')
        
        self.choices = AttrsDef.E_SHAPE
        
        il = get_root_window(self).image_list['node_shape']
        self.m_list.AssignImageList(il, 0)

        # Change dialog size to fit the image size.        
        w, h = il.GetBitmap(0).GetSize()
        if os.sys.platform in ['win32', 'win64']:
            self.SetSize(int(w*4.5), h*4)
        elif os.sys.platform == 'darwin':
            self.SetSize(int(w*6), h*5)
        elif os.sys.platform[:5] == 'linux':
            self.SetSize(int(w*4.5), h*4)
        else:
            self.SetSize(int(w*4.5), h*4)
        
        for x in range(len(self.choices)):
            c = self.choices[x]
            self.m_list.InsertItem(x, c, x)
        
        self.m_list.Bind(wx.EVT_LEFT_DCLICK, self.onOK)
        
        return

    def SetSelectedString(self, nodeshape):
        
        idx = self.m_list.FindItem(0, nodeshape)
        if idx < 0:
            return False
        
        self.m_list.Select(idx, True)
        self.m_list.Focus(idx)
        return True

    def GetSelectedString(self):
        idx = self.m_list.GetFirstSelected()
        if idx == -1:
            return None
        
        return self.m_list.GetItemText(idx)
    
    def onOK(self, event):
        idx = self.m_list.GetFirstSelected()
        if idx == -1:
            return
        
        self.EndModal(wx.ID_OK)
        
class ATDialog(ArrowTypeDialog):
    '''A Dialog to select arrow type.'''
    @staticmethod
    def get_dialog(parent):
        '''A factory method to return singleton.'''
        global AT_DIALOG
        if AT_DIALOG is None:
            AT_DIALOG = ATDialog(parent)
        
        return AT_DIALOG
    
    def __init__(self, parent):
        ArrowTypeDialog.__init__(self, parent)
        self.base_at_list = AttrsDef.E_ARROWTYPE
        
        il = get_root_window(self).image_list['arrow_style']
        self.m_list.AssignImageList(il, 0)

        # Change dialog size to fit the image size.        
        w, h = il.GetBitmap(0).GetSize()
        if os.sys.platform in ['win32', 'win64']:
            self.SetSize(int(w*7), h*6.5)
        elif os.sys.platform == 'darwin':
            self.SetSize(int(w*7), h*6.5)
        else:
            self.SetSize(int(w*7), h*6.5)
        
        
        for x in range(len(self.base_at_list )):
            c = self.base_at_list[x]
            self.m_list.InsertItem(x, c, x)
        
        self.m_list.Bind(wx.EVT_LEFT_DCLICK, self.onOK)
        self.refresh_preview()

    def getArrowType(self):
        
        # Get value from UI.
        ta = self.m_list.GetFirstSelected()
        if ta == -1:
            return None
        
        v_side =  self.m_radioBox_arrowpart.GetSelection()
        v_o = self.m_checkBox_arrowfilled.GetValue()
        
        # Generate arrow type string.
        s_o = ''
        if v_o == False: s_o ='o'
        s_side = ''
        if v_side == 1:
            s_side = 'l'
        elif v_side == 2:
            s_side = 'r'
        s_ta = self.base_at_list[ta]
        
        return ''.join([s_o, s_side, s_ta])
    
    def setArrayType(self, str_arraytype):
        sa = str_arraytype.lower()
        
        ### Let begin a stupid yacc program :)
        is_filled = True
        l_side = ""
        at = ''
        if sa[0] == 'o':
            is_filled = False
            if sa[1] in ['l', 'r']:
                l_side = sa[1]
                at = sa[2:]
            else:
                at = sa[1:]
        elif sa[0] in ['l', 'r']:
            l_side = sa[0]
            at = sa[1:]
        else:
            at = sa
        
        self.m_checkBox_arrowfilled.SetValue(is_filled)
        
        if l_side == "":
            self.m_radioBox_arrowpart.SetSelection(0)
        elif l_side == 'l':
            self.m_radioBox_arrowpart.SetSelection(1)
        else:
            self.m_radioBox_arrowpart.SetSelection(2)
        
        idx = self.base_at_list.index(at)
        self.m_list.Select(idx, True)    
        self.m_list.Focus(idx)
        
        return

    def onATSelected(self, event):
        i = self.m_list.GetFirstSelected()
        if i == -1:
            return None
        at_s = self.base_at_list[i]
        
        ### Do some limit as the official document.
        ### (http://www.graphviz.org/content/arrow-shapes)
        if at_s in ['crow', 'curve', 'icurve', 'tee', 'vee']:
            self.m_checkBox_arrowfilled.SetValue(True)
            self.m_checkBox_arrowfilled.Disable()
        else:
            self.m_checkBox_arrowfilled.Enable()
            
        if at_s in ['dot']:
            self.m_radioBox_arrowpart.SetSelection(0)
            self.m_radioBox_arrowpart.Disable()
        else:
            self.m_radioBox_arrowpart.Enable()
    
        self.refresh_preview()
    
    def onArrowChanged(self, event):
        self.refresh_preview()
    
    def refresh_preview(self):
        
        # Gen image.
        at = self.getArrowType()
        fn = tempfile.gettempdir()+'/atpreview.png'
        DEUtils.gen_arrow_image(at, fn)
        img = wx.Image(fn)
        
        # Cut the center part for preview. 
        w,h=img.GetSize()
        # img = img.GetSubImage(wx.Rect((w-h)/2, 0, w, h))
        
        self.m_bitmap_preview.SetSize((w,h))
        self.m_bitmap_preview.SetBitmap(img.ConvertToBitmap())
        self.m_bitmap_preview.UpdateWindowUI()
        
        return
    
    def onOK(self, event):
        idx = self.m_list.GetFirstSelected()
        if idx == -1:
            return
        
        self.EndModal(wx.ID_OK)


class DotStringProperty(wxpg.PGProperty):
    '''
    Why this? This class existed because the build-in wxpg.PyStringProperty not trigger event when zero-length string input. 
    '''
    def __init__(self, label, name=wxpg.PG_LABEL, value=''):
        wxpg.PGProperty.__init__(self, label, name)
        self.SetValue(value)
        
    def GetClassName(self):
        return 'DotStringProperty'

    def GetEditor(self):
        return 'TextCtrl'
    
    def ValueToString(self, v, flags):
        if len(v):
            return str(v.strip())
        else:
            return ''

    def StringToValue(self, s, flags):
        return True, s

    def ValidateValue(self, value, validationInfo):
        """ Let's limit the value NOT inclue double-quote.
        """
        
        if type(DEUtils.escape_dot_string(value)) == str:
            return True
        else:
            return False


class DotBigStringProperty(DotStringProperty):
    '''
    A PG to edit big text such as label.
    '''
    def GetClassName(self):
        return 'DotBigStringProperty'

    def GetEditor(self):
        return 'TextCtrlAndButton'
    
    def OnEvent(self, propgrid, primaryEditor, event):
        
        ok = False
        
        if event.GetEventType() in [wx.wxEVT_BUTTON, wx.wxEVT_LEFT_UP, wx.wxEVT_RIGHT_UP]:

            dlg = DialogTextEditor(propgrid)
            dlg.SetTitle('Input the label text')

            text = self.GetValueAsString()
            dlg.m_text.SetValue(text)
    
            if dlg.ShowModal() == wx.ID_OK:
                text = dlg.m_text.GetValue()
                self.m_value = text
                self.SetValueInEvent(text)
                ok = True
            
            elif dlg.ShowModal() in [wx.ID_CANCEL, wx.ID_EXIT]:
                self.m_value = None
            
        
        return ok


class DotFloatProperty(wxpg.FloatProperty):
    
    def ValueToString(self, v, flags):
        if len(v):
            c_str = str(v.strip().lower())
            ### If no decimal point, add .0
            if c_str.isdigit():
                c_str += '.0'
            return c_str
        else:
            return ''
    
    # def DoGetValue(self):
    #     return self.ValueToString(self.m_value, None)

class DotColorSchemeProperty(wxpg.PGProperty):
    def __init__(self, label, name=wxpg.PG_LABEL, value=''):
        wxpg.PGProperty.__init__(self, label, name)
        self.choices = AttrsDef.E_COLORSCHEME
        self.SetValue(value)
    
    def GetClassName(self):
        return 'DotColorSchemeProperty'
    
    def GetEditor(self):
        return "TextCtrlAndButton"
        
    def StringToValue(self, s, flags):
        s = s.strip().lower()
        if s in self.choices:
            return True, s
        
        return False

    def ValueToString(self, v, flags):
        if len(v):
            return str(v.strip().lower())
        else:
            return ''
    
    def OnEvent(self, propgrid, primaryEditor, event):
        
        ok = False
        
        if event.GetEventType() in [wx.wxEVT_BUTTON, wx.wxEVT_LEFT_UP, wx.wxEVT_RIGHT_UP]:

            dlg = CSDialog.get_dialog(propgrid)
    
            if dlg.ShowModal() == wx.ID_OK:
                cs = dlg.GetColorScheme()
                self.m_value = cs
                self.SetValueInEvent(cs)
                ok = True
            
            elif dlg.ShowModal() in [wx.ID_CANCEL, wx.ID_EXIT]:
                self.m_value = None
            
            if isinstance(self.m_value, str):
                dlg.SetColorScheme(self.m_value)
            
        return ok

class DotColorProperty(wxpg.PGProperty):
    '''The value of pg should be 3 type:
        1. A color name in string.
        2. A RGB/RGBA value in tuple(r,g,b in 0~255).
        3. A int to point out the index in colorscheme. 
    '''

    def __init__(self, label, name=wxpg.PG_LABEL, value=''):
        wxpg.PGProperty.__init__(self, label, name)
        self.SetValue(value)
    
    def GetClassName(self):
        return 'DotColorProperty'
    
    def GetEditor(self):
        return "TextCtrlAndButton"
    
    def StringToValue(self, s, flags):
        
        s = remove_double_quote(s).strip()

        # For emtpy value.
        if s == '': 
            return True, None
        
        # Try to parse hex string.
        if s[0] == '#':
            try:
                if len(s) == 7: # RGB.
                    r, g, b = colour.hex2rgb(s)
                    return True, (255*r,255*g,255*b)
                elif len(s) == 9: # RGBA.
                    r, g, b = colour.hex2rgb(s[:-2])
                    a = int(s[-2:], 16)
                    return True, (255*r,255*g,255*b,a)
                else:
                    return False
            except:
                return False
        
        # Try to parse HSV string.
        elif s[0].isdigit() or s[0] == '.': # Try to parse numbers
            try:
                # If get single int value.
                if s.isdigit():
                    return True, int(s)
                else:
                    h,s,v = map(float, s.split(' '))
                    rgb = wx.Image.HSVtoRGB(wx.Image_HSVValue(h,s,v))
                    return True, (rgb.red, rgb.green, rgb.blue)
            except:
                return False
            
        # Color in string.
        else:
            scheme = self.__get_current_scheme()
            if scheme is None:
                return True, s
            
            colors = get_colors_in_scheme(scheme).keys()
            
            if s.strip() not in colors:
                return False
            
            return True, get_colors_in_scheme(scheme)[s]

    def ValueToString(self, value, flags):

        if value is None or len(value) == 0:
            return ''
        
        if isinstance(value, str):
            return str(value.strip().lower())
        elif isinstance(value, int):
            return str(value.strip().lower())
        elif isinstance(value, tuple):
            if len(value) == 3:
                return '#%02x%02x%02x'%value
            elif len(value) == 4:
                return '#%02x%02x%02x%02x'%value
            else:
                return ''
        else:
            return ''

    def __get_current_scheme(self):
        # Get the colorscheme in the same propgrid.
        grid = self.GetGrid()
        if grid is None:
            return None
        cs_pg = grid.GetPropertyByLabel('colorscheme')
        if cs_pg is None:
            return None
            
        scheme = cs_pg.GetValue().lower().strip()
        
        return scheme

    def OnEvent(self, propgrid, primaryEditor, event):
        if event.GetEventType() in [wx.wxEVT_BUTTON, wx.wxEVT_LEFT_UP, wx.wxEVT_RIGHT_UP]:

            scheme = self.__get_current_scheme()
            if scheme is None:
                scheme = 'x11'
            
            dlg = CSCDialog(propgrid, scheme)

            if dlg.ShowModal() == wx.ID_OK:
                color = dlg.GetColorString()
                self.m_value = color
                self.SetValueInEvent(color)
                return True
            
            elif dlg.ShowModal() in [wx.ID_CANCEL, wx.ID_EXIT]:
                self.m_value = None
            
            if isinstance(self.m_value, str):
                dlg.SetColorString(self.m_value)
            
        return False    
    
    def SetChoices(self, choices):
        self.choices = choices
        
    # def DoGetValue(self):
    #     return self.ValueToString(self.m_value, None)

class DotEnumProperty(wxpg.PGProperty):
    
    def __init__(self, label, name=wxpg.PG_LABEL, value=''):
        wxpg.PGProperty.__init__(self, label, name)
        self.SetValue(value)
    
    def GetClassName(self):
        return 'DotEnumProperty'
    
    def GetEditor(self):
        return "ComboBox"

    def StringToValue(self, s, flags):
        if s == '' or (s in self.GetChoices().GetLabels()) or (s.upper() in self.GetChoices().GetLabels()) or (s.lower() in self.GetChoices().GetLabels()):
            return True, s
        else:
            return False
         
    def ValueToString(self, value, flags):
        try:
            if len(value):
                return str(value.strip())
            else:
                return ''
        except:
            print("Error Line 655 for value - ",value,type(value))


class DotEnumCombineProperty(wxpg.PGProperty):
    
    def __init__(self, label, name=wxpg.PG_LABEL, value=''):
        wxpg.PGProperty.__init__(self, label, name)
        self.SetValue(value)
        
    def GetClassName(self):
        return 'DotEnumCombineProperty'
    
    def GetEditor(self):
        return "TextCtrlAndButton"

    def OnEvent(self, propgrid, primaryEditor, event):
        
        if event.GetEventType() in [wx.wxEVT_BUTTON, wx.wxEVT_LEFT_UP, wx.wxEVT_RIGHT_UP]:
            
            dlg = wx.MultiChoiceDialog(propgrid, message='Check all wanted %ss below:'%self.GetLabel(),
                                        caption='Make Choices', choices=self.choices.GetLabels())

            if dlg.ShowModal() == wx.ID_OK:
                sels = dlg.GetSelections()
                v = ''
                if len(sels) == 0:
                    self.m_value = ''
                    # return True
                else:
                    for idx in sels:
                        v += self.choices.GetLabels()[idx] +', '
                    v = v[:-2]

                self.m_value = v
                self.SetValueInEvent(v)
                return True
            
            elif dlg.ShowModal() in [wx.ID_CANCEL, wx.ID_EXIT]:
                self.m_value = None
            
            if self.m_value:
                if len(self.m_value.strip()) > 0:
                    sels = [ self.choices.index(x.strip()) for x in self.m_value.split(',') ]
                    dlg.SetSelections(sels)
                
        return False    
        
    def SetChoices(self, choices):
        self.choices = choices

    def StringToValue(self, s, flags):
        
        s = s.strip()
        if s == '':
            return True, s
    
        styles = s.split(',')
        for sty in styles:
            if sty.strip() not in self.choices.GetLabels():
                return False
        
        return True, s
    
    def ValueToString(self, value, flags):
        if len(value):
            return str(value.strip().lower())
        else:
            return ''


class DotEnumChoiceProperty(wxpg.PGProperty):
    
    def __init__(self, label, name=wxpg.PG_LABEL, value=''):
        wxpg.PGProperty.__init__(self, label, name)
        self.SetValue(value)
        
    def GetClassName(self):
        return 'DotEnumChoiceProperty'
    
    def GetEditor(self):
        return "TextCtrlAndButton"

    def OnEvent(self, propgrid, primaryEditor, event):
        
        if event.GetEventType() in [wx.wxEVT_BUTTON, wx.wxEVT_LEFT_UP, wx.wxEVT_RIGHT_UP]:
            
            dlg = wx.SingleChoiceDialog(propgrid, message='Check wanted %s below:'%self.GetLabel(),
                                        caption='Make Choice', choices=self.choices.GetLabels())

            if dlg.ShowModal() == wx.ID_OK:
                sels = dlg.GetSelection()
                v = self.choices.GetLabels()[sels]
                self.m_value = v
                self.SetValueInEvent(v)
                return True
            
            elif dlg.ShowModal() in [wx.ID_CANCEL, wx.ID_EXIT]:
                self.m_value = None
            
            if self.m_value:
                dlg.SetSelection(self.m_value.strip())
                
        return False
        
    def SetChoices(self, choices):
        self.choices = choices

    def StringToValue(self, s, flags):
        
        s = s.strip()
        if s == '':
            return True, s
    
        if s.strip() not in self.choices.GetLabels():
                return False
        
        return True, s
    
    def ValueToString(self, value, flags):
        if len(value):
            return str(value.strip().lower())
        else:
            return ''


class DotEnumNodeShapeProperty(wxpg.PGProperty):
    
    def __init__(self, label, name=wxpg.PG_LABEL, value=''):
        wxpg.PGProperty.__init__(self, label, name)
        self.choices = AttrsDef.E_SHAPE
        self.SetValue(value)
        
    def GetClassName(self):
        return 'DotEnumNodeShapeProperty'
    
    def GetEditor(self):
        return "TextCtrlAndButton"

    def OnEvent(self, propgrid, primaryEditor, event):
        if event.GetEventType() in [wx.wxEVT_BUTTON, wx.wxEVT_LEFT_UP, wx.wxEVT_RIGHT_UP]:
            dlg = NodeShapeDialog.get_dialog(propgrid)
            
            if dlg.ShowModal() == wx.ID_OK:
                v = dlg.GetSelectedString()
                self.m_value = v
                self.SetValueInEvent(v)
                return True
            
            elif dlg.ShowModal() in [wx.ID_CANCEL, wx.ID_EXIT]:
                self.m_value = None
            
            # Set the current value.
            if self.m_value:
                dlg.SetSelectedString(self.m_value)
            
        return False    

    def StringToValue(self, s, flags):

        s = s.strip()

        if s == '' or s in self.choices:
            return True, s
        else:
            return False
        
        return False
    
    def ValueToString(self, value, flags):

        if len(value):
            return str(value.strip().lower())
        else:
            return ''
    

class DotEnumArrowTypeProperty(wxpg.PGProperty):
    
    def __init__(self, label, name=wxpg.PG_LABEL, value=''):
        wxpg.PGProperty.__init__(self, label, name)
        self.SetValue(value)
        
    def GetClassName(self):
        return 'DotEnumArrowTypeProperty'
    
    def GetEditor(self):
        return "TextCtrlAndButton"

    def OnEvent(self, propgrid, primaryEditor, event):
        if event.GetEventType() in [wx.wxEVT_BUTTON, wx.wxEVT_LEFT_UP, wx.wxEVT_RIGHT_UP]:
            
            dlg = ATDialog.get_dialog(propgrid)
            
            if dlg.ShowModal() == wx.ID_OK:
                v = dlg.getArrowType()
                self.m_value = v
                self.SetValueInEvent(v)
                return True
            
            elif dlg.ShowModal() in [wx.ID_CANCEL, wx.ID_EXIT]:
                self.m_value = None
            
            # Show the current arrow_type in m_value.
            if self.m_value:
                dlg.setArrayType(self.m_value)
            
        return False    

    def StringToValue(self, s, flags):

        s = s.strip()
        a_names = AttrsDef.E_ARROWTYPE
        test = re.compile(r'(?i)o{0,1}(l|r){0,1}(%s)\b'%('|'.join(a_names)))
        if test.match(s) is None:
            return False
        else:
            return True, s
    
    def ValueToString(self, value, flags):
        if len(value):
            return str(value.strip().lower())
        else:
            return ''


class DotEditEnumProperty(wxpg.StringProperty):
    
    def GetEditor(self):
        return "ComboBox"
    
map_type2class = {'string':         DotStringProperty, 
                  'bigstring':      DotBigStringProperty,
                  'int':            wxpg.UIntProperty,
                  'bool':           wxpg.BoolProperty,
                  'float':          DotFloatProperty,
                  'color':          DotColorProperty,
                  'colorscheme':    DotColorSchemeProperty,
                  'enum':           DotEnumProperty,
                  'enum_choice':    DotEnumChoiceProperty,
                  'enum_edit':      DotEditEnumProperty,
                  'enum_combine':   DotEnumCombineProperty,
                  'enum_nodeshape': DotEnumNodeShapeProperty,
                  'enum_arrowtype': DotEnumArrowTypeProperty,
                  'img_file':       wxpg.ImageFileProperty, 
                  } 


def buildPG(attr_name, g_type):
    '''Build PropGridProperty instance by attr_name and g_type.'''
    info = AttrsDef.get_dot_attr(attr_name, g_type)
    pg_class = map_type2class[info['type']]
    
    pg_item = pg_class(attr_name)
    if info['type'] in ['enum', 'enum_edit', 'enum_combine', 'enum_choice']:
        try:
            pg_item.SetChoices(wx.propgrid.PGChoices(info['param']))
        except:
            print("Error Line 827 - Set Choices Param:{}\tType:{}\tAttr-{}".format(info['param'],info['type'],attr_name))
    
    elif info['type'] == 'bool':
       pg_item.SetEditor('CheckBox')
    
    elif info['type'] == 'img_file':
        pg_item.SetAttribute(wxpg.PG_FILE_WILDCARD, 
                             "Support Image File (*.png;*.gif)|*.png;*.gif"+\
                             "|PNG File (*.png)|*.png"+\
                             "|Gif File (*.gif)|*.gif")
    
    v = info['default_value']
    
    if v is None:
        pg_item.SetDefaultValue(None)
    else:
        if info['type'] == 'bool':
            bv = False
            if v in [True, 'true', '1', 1]:
                bv = True
            pg_item.SetDefaultValue(bv)
            pg_item.SetValue(bv)
        
        else:
            pg_item.SetDefaultValue(str(v).strip())
            pg_item.SetValue(str(v))
            

    pg_item.SetHelpString(info['description'])
    
    return pg_item
    
    