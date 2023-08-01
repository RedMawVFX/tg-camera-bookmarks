from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import asksaveasfile
from tkinter.filedialog import askopenfile
import re
import terragen_rpc as tg

def display_bookmarks():    
    popup_info("Bookmark values",bookmarks)

def reset_bookmarks():
    # Python drops to global if local vars not defined
    global bookmarks
    bookmarks = [(default_position,default_rotation,default_focal)] * 10
    my_messages.set("Bookmarks reset to default values.")

def reset_bookmarks_zero(): 
    global bookmarks
    zero = '0 0 0'   
    bookmarks = [(zero,zero,default_focal)] * 10
    my_messages.set("Bookmarks rest to 0,0,0")

def popup_help_file_menu():
    text = "Open bookmarks: Replaces all existing bookmarks with values loaded from file. \nSave bookmarks: Saves all current bookmark values to a file."
    popup_info("Help for File menu", text)

def popup_help_utility_menu():
    text = "Display bookmarks: Displays the current values assigned to all the bookmarks. \nRest bookmarks: Resets all bookmarks to default render camera values. \nReset bookmarks to zero: Resets all bookmark postion and rotation values to zero."  
    popup_info("Help for Utility menu",text)  
        

gui = Tk()
gui.title("tg_camera_bookmark")
gui.geometry("600x500")

gui.columnconfigure(0,weight=1)
gui.columnconfigure(1,weight=2)

gui.rowconfigure(0,weight=1)
gui.rowconfigure(1,weight=1)
gui.rowconfigure(2,weight=1)
gui.rowconfigure(3,weight=4)

frame0 = LabelFrame(gui,text="Select active bookmark")
frame1 = LabelFrame(gui,text="Copy bookmark from")
frame2 = LabelFrame(gui,text="Apply bookmark to")
frame3 = LabelFrame(gui,text="Messages:",bg="#FFF9EC",relief=FLAT)

frame0.grid(row=0,column=0,sticky="WENS",padx=10,pady=10)
frame1.grid(row=1, column=0,sticky="WENS",padx=10,pady=10)
frame2.grid(row=2, column=0,sticky="WENS",padx=10,pady=10)
frame3.grid(row=3,column=0,sticky="WENS",padx=10,pady=10)

error_table = {
1: "Terragen RPC connection error",
2: "Terragen RPC timeout error",
3: "Terragen RPC server reply error",
4: "Terragen RPC API error",
5: "Terragen RPC attribute error"
}

def get_cameras():
    try:
        project = tg.root()
        node_ids = tg.children_filtered_by_class(project,'camera')
        return(node_ids)
    except ConnectionError as e:
        popup_message(1,str(e))
    except TimeoutError as e:
        popup_message(2,str(e))
    except tg.ReplyError as e:
        popup_message(3,str(e))
    except tg.ApiError:
        popup_message(4,str(e))

def update_combobox_cameras():
    r = get_cameras()    
    create_camera_dictionary(r)
    acquire_camera_cb["values"] = list(camera_dictionary.values())
    acquire_camera_cb.current(0)
    apply_camera_cb["values"] = list(camera_dictionary.values())
    apply_camera_cb.current(0)

def popup_info(message_title,message_description):
    messagebox.showinfo(title=message_title,message=message_description)

def popup_message(message_type,message_description):
    messagebox.showwarning(title=error_table[message_type], message = message_description)

def popup_add_camera(message_type,message_description):
    user_choice = messagebox.askyesno(title = message_type,message=message_description)
    if user_choice:
        add_camera()

def add_camera():
    try:
        project = tg.root()
        tg.create_child(project,'camera')
    except ConnectionError as e:
        popup_message(1,str(e))
    except TimeoutError as e:
        popup_message(2,str(e))
    except tg.ReplyError as e:
        popup_message(3,str(e))
    except tg.ApiError:
        popup_message(4,str(e))

def create_camera_dictionary(ids):
    camera_dictionary.clear()
    for nodes in ids:
        # print ("nodes ",nodes)
        try:
            camera_dictionary[str(nodes)]= tg.name(nodes)
        except ConnectionError as e:
            popup_message(1,str(e))
        except TimeoutError as e:
            popup_message(2,str(e))
        except tg.ReplyError as e:
            popup_message(3,str(e))
        except tg.ApiError:
            popup_message(4,str(e))

def set_bookmark_rb():
    x = bookmark_rb.get()    

def acquire_bookmark():
    camera_params_as_list = []
    rb_selection = bookmark_rb.get()    
    camera_selection = acquire_from_camera.get()
    selected_camera_position, selected_camera_rotation, selected_camera_focal = get_camera_params(camera_selection)    
    camera_params_as_string = str(selected_camera_position),str(selected_camera_rotation),str(selected_camera_focal)    
    bookmarks[rb_selection-1] = camera_params_as_string
    build_message("acquire",rb_selection,camera_selection)    

def build_message(x,rb,cam):
    if x == "acquire":
        y = str(cam) + " applied to bookmark " + str(rb) + " "
        my_messages.set(y)
    elif x == "apply":
        y = "Bookmark " + str(rb+1) + " applied to " +str (cam) + " "
        my_messages.set(y)
    elif x == "loaded":
        y = "Bookmarks loaded from disk "
        my_messages.set(y)
    elif x == "saved":
        y = "Bookmarks saved to disk "
        my_messages.set(y)

def get_camera_params(x):
    try:
        node = tg.node_by_path(x)
        pos = node.get_param('position')
        rot = node.get_param('rotation')
        foc = node.get_param('focal_length_in_mm') 
        return pos,rot,foc
    except ConnectionError as e:
        popup_message(1,str(e))
    except TimeoutError as e:
        popup_message(2,str(e))
    except tg.ReplyError as e:
        popup_message(3,str(e))
    except tg.ApiError:
        popup_message(4,str(e))

def set_camera_params(cam,book):    
    preset = bookmarks[book]
    try:
        node = tg.node_by_path(cam)    
        node.set_param('position',preset[0])
        node.set_param('rotation',preset[1])
        node.set_param('focal_length_in_mm',preset[2])
    except ConnectionError as e:
        popup_message(1,str(e))
    except TimeoutError as e:
        popup_message(2,str(e))
    except tg.ReplyError as e:
        popup_message(3,str(e))
    except tg.ApiError:
        popup_message(4,str(e))
    
def print_bookmark_data(x,y,z): # old
    for i in range(10):
       print ("position is ",x)
       print ("rotaion is ",y)
       print ("focual is ",z)

def apply_bookmark():    
    rb_selection = bookmark_rb.get()    
    camera_selection = apply_to_camera.get()    
    set_camera_params(camera_selection,rb_selection-1)
    build_message("apply",rb_selection-1,camera_selection)  
    
def save_bookmarks_to_disk():    
    my_filetypes = [("Text document","*.txt"),("All files","*.*")]
    file = asksaveasfile(filetypes= my_filetypes, defaultextension=my_filetypes)    
    x = str(bookmarks)    
    file.write(x)
    file.close()
    build_message("saved"," "," ")

def load_bookmarks_from_disk():
    global bookmarks
    presets_from_disk = read_from_file()    
    formatted_presets = format_presets_from_disk(presets_from_disk)    
    bookmarks = formatted_presets   
    

def format_presets_from_disk(presets):
    converted_string = str(presets)
    pattern = r"\(.*?\)"
    matches = re.findall(pattern,converted_string)
    extracted_elements = [eval(match) for match in matches]    
    return extracted_elements
                    
def read_from_file():    
    my_filetypes = [("Text document","*.txt"),("All files","*.*")]
    file = askopenfile(mode='r',filetypes= my_filetypes)
    content = file.read()    
    file.close()
    return content


# variables
camera_dictionary = {}
acquire_from_camera = StringVar()
apply_to_camera = StringVar()
bookmark_rb = IntVar()
bookmark_rb.set(1)
default_position = '0 10 -30'
default_rotation = '-7 0 0'
default_focal = '31.1769'
bookmarks = [(default_position,default_rotation,default_focal)] * 10
my_messages =StringVar()
my_messages.set("Welcome.  ")

# menu bar
menubar = Menu(gui)
filemenu = Menu(menubar,tearoff=0)
filemenu.add_command(label="Open bookmarks...",command=load_bookmarks_from_disk)
filemenu.add_command(label="Save bookmarks...",command = save_bookmarks_to_disk)
menubar.add_cascade(label="File",menu=filemenu)

utilitymenu = Menu(menubar,tearoff=0)
utilitymenu.add_command(label = "Display bookmarks", command=display_bookmarks)
utilitymenu.add_separator()
utilitymenu.add_command(label="Reset bookmarks",command=reset_bookmarks)
utilitymenu.add_command(label="Reset bookmarks to zero",command=reset_bookmarks_zero)
menubar.add_cascade(label="Utility",menu=utilitymenu)

helpmenu = Menu(menubar,tearoff=0)
# At a later date, combine these help options into a single function or two
helpmenu.add_command(label="For file menu",command=popup_help_file_menu)
helpmenu.add_command(label="For utility menu",command=popup_help_utility_menu)
menubar.add_cascade(label="Help",menu=helpmenu)

# main
camera_ids = get_cameras()
# print(camera_ids)
if not camera_ids:
    popup_add_camera("Add Camera","Add Camera node to project?")
    camera_ids = get_cameras()
    if not camera_ids:
        quit()
# build camera dictionary
create_camera_dictionary(camera_ids)

# radio buttons
bookmark_01_rb = Radiobutton(frame0,text="Bookmark 01",variable=bookmark_rb,value=1,command=set_bookmark_rb).grid(row=0,column=0)
bookmark_02_rb = Radiobutton(frame0,text="Bookmark 02",variable=bookmark_rb,value=2,command=set_bookmark_rb).grid(row=0,column=1)
bookmark_03_rb = Radiobutton(frame0,text="Bookmark 03",variable=bookmark_rb,value=3,command=set_bookmark_rb).grid(row=0,column=2)
bookmark_04_rb = Radiobutton(frame0,text="Bookmark 04",variable=bookmark_rb,value=4,command=set_bookmark_rb).grid(row=0,column=3)
bookmark_05_rb = Radiobutton(frame0,text="Bookmark 05",variable=bookmark_rb,value=5,command=set_bookmark_rb).grid(row=0,column=4)

bookmark_06_rb = Radiobutton(frame0,text="Bookmark 06",variable=bookmark_rb,value=6,command=set_bookmark_rb).grid(row=1,column=0)
bookmark_07_rb = Radiobutton(frame0,text="Bookmark 07",variable=bookmark_rb,value=7,command=set_bookmark_rb).grid(row=1,column=1)
bookmark_08_rb = Radiobutton(frame0,text="Bookmark 08",variable=bookmark_rb,value=8,command=set_bookmark_rb).grid(row=1,column=2)
bookmark_09_rb = Radiobutton(frame0,text="Bookmark 09",variable=bookmark_rb,value=9,command=set_bookmark_rb).grid(row=1,column=3)
bookmark_10_rb = Radiobutton(frame0,text="Bookmark 10",variable=bookmark_rb,value=10,command=set_bookmark_rb).grid(row=1,column=4)


# labels and combobox
acquire_instructions = Label(frame1,text='Select camera or refresh list.',relief = FLAT,padx=20,pady=10).grid(row = 0,column=0,sticky='w')
apply_instructions = Label(frame2,text='Select camera or refresh list.',relief = FLAT,padx=20,pady=10).grid(row = 0,column=0,sticky='w')

acquire_camera_cb = ttk.Combobox(frame1,textvariable=acquire_from_camera,postcommand=update_combobox_cameras)
acquire_camera_cb["values"] = list(camera_dictionary.values())
acquire_camera_cb.current(0)
acquire_camera_cb.grid(row=0,column=1)

apply_camera_cb = ttk.Combobox(frame2,textvariable=apply_to_camera,postcommand=update_combobox_cameras)
apply_camera_cb["values"] = list(camera_dictionary.values())
apply_camera_cb.current(0)
apply_camera_cb.grid(row=0,column=1)

null = Label(frame1,text=" ").grid(row=3,columnspan=2)
null_02 = Label(frame2,text=" ").grid(row=3,columnspan=2)

info_message = Label(frame3,textvariable=my_messages,fg='red',bg="#FFF9EC",padx=4).grid(row=0,columnspan=2,sticky='wens')

# buttons
acquire_camera_button = Button(frame1,text="COPY bookmark",bg="#BED5F4",command=acquire_bookmark,padx=10,pady=5).grid(row=2,column=0)
apply_camera_button = Button(frame2,text="APPLY bookmark",bg='#BEF4C2',command=apply_bookmark,padx=10,pady=5).grid(row=2,column=0)

gui.config(menu=menubar)
gui.mainloop()