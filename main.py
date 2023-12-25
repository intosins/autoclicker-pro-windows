import threading, time, json, keyboard, mouse, pygame

import customtkinter
from customtkinter import CTk, CTkLabel, CTkButton, CTkFrame, CTkEntry, CTkOptionMenu, CTkCheckBox, StringVar, IntVar, END

from tkinter import messagebox

root = CTk()
root.attributes('-topmost', False)
root.iconbitmap('images/icon.ico')

customtkinter.set_appearance_mode('Dark')

version = '1.9'

config_json_path = 'config.json'

clicking = False
cps = 10
repeat = 0
hotkey = 'f6'
hotkey_recording = False
selected_mouse_button = 'Left'
selected_click_type = 'Single'
window_width = 400
window_height = 400

repeat_until_stopped_enabled = True
repeat_until_stopped = IntVar(value=1)

esc_ref = None
esc = IntVar(value=0)

show = IntVar(value=0)

window_save = True
window = IntVar(value=1)

sound_enabled = False
sound = IntVar(value=0)

labels = IntVar(value=0)

theme = IntVar(value=0)

lp2_visible = False

mouse_button_options = ['Left', 'Right', 'Middle']
selected_mouse_button_var = StringVar(value=selected_mouse_button)

click_type_options = ['Single', 'Double', 'Triple', 'Quadruple']
selected_click_type_var = StringVar(value=selected_click_type)

pygame.mixer.init()

def update_window_title():
    if clicking:
        root.title('Autoclicker Pro (ON)')
    else:
        root.title('Autoclicker Pro (OFF)')

update_window_title()

def closing():
    global clicking
    if clicking:
        clicking = False
        update_window_title()
        if autoclick_thread is not None and autoclick_thread.is_alive():
            autoclick_thread.join()
    if messagebox.askokcancel('Quit', 'Are u sure that u want to quit?'):
        save_settings()
        root.destroy()

def save_settings():
    global window_save
    settings = {
        'cps': max(1, min(cps, 2000)),
        'repeat': repeat,
        'hotkey': hotkey,
        'selected_mouse_button': selected_mouse_button,
        'selected_click_type': selected_click_type,
        # 'window_width': root.winfo_width(),
        # 'window_height': root.winfo_height()
    }

    if window_save:
        settings['window_width'] = root.winfo_width()
        settings['window_height'] = root.winfo_height()

    with open(config_json_path, 'w') as f:
        json.dump(settings, f, indent=4)

def load_settings():
    global clicking, cps, hotkey, selected_mouse_button, selected_click_type, theme, window_width, window_height, repeat
    try:
        with open(config_json_path, 'r') as f:
            settings = json.load(f)

            cps = max(1, min(settings.get('cps', 10), 2000))
            repeat = settings.get('repeat', 0)
            hotkey = settings.get('hotkey', 'f6')

            loaded_mouse_button = settings.get('selected_mouse_button', 'Left')
            selected_mouse_button_var.set(loaded_mouse_button)
            selected_mouse_button = loaded_mouse_button
            
            loaded_click_type = settings.get('selected_click_type', 'Single')
            selected_click_type_var.set(loaded_click_type)
            selected_click_type = loaded_click_type

            window_width = settings.get('window_width', root.winfo_width())
            window_height = settings.get('window_height', root.winfo_height())
    except json.decoder.JSONDecodeError:
        cps = 10
        repeat = 0
        hotkey = 'f6'
        selected_mouse_button = 'Left'
        selected_click_type = 'Single'
        window_width = 400
        window_height = 400
    except FileNotFoundError:
        with open(config_json_path, 'w') as f:
            f.write(json.dumps({
                'cps': cps,
                'repeat': repeat,
                'hotkey': hotkey,
                'selected_mouse_button': selected_mouse_button,
                'selected_click_type': selected_click_type,
                'window_width': 400,
                'window_height': 400
            }, indent=4))

def reset_to_default_settings():
    global clicking, cps, hotkey, selected_mouse_button, selected_click_type, theme, window_width, window_height, selected_click_type_var, selected_mouse_button_var, lp2, lp2_visible, repeat
    if clicking:
        clicking = False
        update_window_title()
        if autoclick_thread is not None and autoclick_thread.is_alive():
            autoclick_thread.join()
    if messagebox.askokcancel('Reset', 'Are u sure that u want to reset autoclicker to default settings?'):
        cps = 10
        repeat = 0
        hotkey = 'f6'
        selected_mouse_button = 'Left'
        selected_mouse_button_var.set('Left')
        selected_click_type = 'Single'
        selected_click_type_var.set('Single')
        window_width = 400
        window_height = 400

        t2.configure(text=('Hotkey: ' + hotkey.upper()))

        v2.delete(0, END)
        v2.insert(0, str(cps))

        r2.delete(0, END)
        r2.insert(0, str(repeat))

        lp2.grid_forget()
        lp2_visible = False

        root.geometry(f"{window_width}x{window_height}")

        save_settings()

def change_mouse_button(selection):
    global selected_mouse_button
    selected_mouse_button = selection
    save_settings()

def change_click_type(selection):
    global selected_click_type
    selected_click_type = selection
    save_settings()

def set_cps():
    global cps
    try:
        new_cps = float(v2.get())
        if int(new_cps) > 2000 or int(new_cps) < 0:
            cps = 10

            v2.delete(0, END)
            v2.insert(0, str(cps))

            messagebox.showerror('Error', 'CPS cannot be set above 2,000.')
        else:
            cps = int(new_cps)
            save_settings()
    except ValueError:
        cps = 10
            
        v2.delete(0, END)
        v2.insert(0, str(cps))
        
        messagebox.showerror('Error', 'Invalid CPS. Please enter a valid number.')

def set_repeat():
    global repeat
    try:
        new_repeat = float(r2.get())
        if int(new_repeat) < 0:
            repeat = 0

            r2.delete(0, END)
            r2.insert(0, str(repeat))

            messagebox.showerror('Error', 'Invalid Repeat. Please enter a valid number.')
        else:
            repeat = int(new_repeat)
            save_settings()
    except ValueError:
        repeat = 0

        r2.delete(0, END)
        r2.insert(0, str(repeat))
        
        messagebox.showerror('Error', 'Invalid Repeat. Please enter a valid number.')

def autoclick():
    global clicking, cps, repeat_until_stopped_enabled, repeat
    while True:
        if clicking and int(cps) >= 0:
            if not repeat_until_stopped_enabled and int(repeat) > 0:
                click()
                repeat -= 1
                if repeat <= 0:
                    clicking = False
                    update_window_title()
                    if autoclick_thread is not None and autoclick_thread.is_alive():
                        autoclick_thread.join()
            else:
                click()
            time.sleep(0.95 / cps)
        else:
            break

def click():
    global sound_enabled
    if selected_click_type == 'Single':
        mouse.click(selected_mouse_button.lower())
        if sound_enabled:
            play_clicking_sound()
    elif selected_click_type == 'Double':
        mouse.double_click(selected_mouse_button.lower())
        if sound_enabled:
            for _ in range(2):
                play_clicking_sound()
        time.sleep(1 / cps)
    elif selected_click_type == 'Triple':
        for _ in range(3):
            mouse.click(selected_mouse_button.lower())
            if sound_enabled:
                play_clicking_sound()
            time.sleep(1 / cps)
    elif selected_click_type == 'Quadruple':
        for _ in range(2):
            mouse.double_click(selected_mouse_button.lower())
            mouse.double_click(selected_mouse_button.lower())
            if sound_enabled:
                for _ in range(4):
                    play_clicking_sound()
            time.sleep(1 / cps)

def turn_on_autoclicker():
    global clicking, autoclick_thread, cps
    if not clicking:
        try:
            if int(cps) > 2000 or int(cps) < 0:
                messagebox.showerror('Error', 'CPS cannot be set above 2,000.')
            else:
                clicking = True

                autoclick_thread = threading.Thread(target=autoclick)
                autoclick_thread.daemon = True
                autoclick_thread.start()

                update_window_title()
        except ValueError:
            messagebox.showerror('Error', 'Invalid CPS. Please enter a valid number.')

def turn_off_autoclicker():
    global clicking, autoclick_thread, cps
    if clicking:
        try:
            if int(cps) > 2000 or int(cps) < 0:
                messagebox.showerror('Error', 'CPS cannot be set above 2,000.')
            else:
                clicking = False

                if autoclick_thread is not None and autoclick_thread.is_alive():
                    autoclick_thread.join()

                autoclick_thread = None

                update_window_title()
        except ValueError:
            messagebox.showerror('Error', 'Invalid CPS. Please enter a valid number.')

def hotkey_autoclicker(event=None):
    global clicking

    # hotkey_pressed = keyboard.is_pressed(hotkey)

    # if hotkey_pressed:
        # other_keys_pressed = any(keyboard.is_pressed(key) for key in keyboard.all_modifiers if key != hotkey)
        # if not other_keys_pressed:
            # if clicking:
                # turn_off_autoclicker()
            # else:
                # turn_on_autoclicker()
        # elif other_keys_pressed:
            # messagebox.showerror('Error', "Don't press other keys when you are enabling autoclicker.")
    
    if keyboard.is_pressed(hotkey):
        if not clicking:
            turn_on_autoclicker()
        else:
            turn_off_autoclicker()

def hotkey_record():
    global hotkey, hotkey_recording
    if not hotkey_recording:
        hotkey_recording = True
        
        t2.configure(text='Press a key to set as hotkey...')
        b1.configure(text='Stop Recording')

        keyboard.unhook_all()
        keyboard.hook(wait_for_key_press)
    else:
        hotkey_recording = False

        if hotkey is not None:
            save_settings()

            t2.configure(text=('Hotkey: ' + hotkey.upper()))

            try:
                keyboard.unhook_key(hotkey)
            except ValueError:
                pass

        b1.configure(text='Change Hotkey')

        keyboard.unhook_all()

def wait_for_key_press(event):
    global hotkey, hotkey_recording
    hotkey = event.name

    t2.configure(text=('Hotkey: ' + hotkey.upper()))
    hotkey_recording = False
    b1.configure(text='Change Hotkey')

    keyboard.unhook_all()
    keyboard.hook_key(hotkey, hotkey_autoclicker)

def display_info():
    messagebox.showinfo('Info', 'Enjoy using the autoclicker! (@intosins)')

def toggle_menu():
    global lp2, lp2_visible
    if lp2_visible:
        root.rowconfigure(1, weight=0)
        lp2.grid_forget()
        lp2_visible = False
    else:
        root.rowconfigure(1, weight=1)
        lp2.grid(row=0, column=1, rowspan=10, padx=(10, 0), sticky='nsew')
        lp2_visible = True

def toggle_esc():
    global esc_ref
    esc_state = esc.get()
    if esc_state == 1:
        esc_ref = keyboard.add_hotkey('esc', turn_off_autoclicker)
    else:
        if esc_ref is not None:
            keyboard.remove_hotkey('esc')

def toggle_show():
    show_state = show.get()
    if show_state == 1:
        root.attributes('-topmost', True)
    else:
        root.attributes('-topmost', False)

def toggle_window_saving_width_height_on_exit():
    global window_save
    window_state = window.get()
    if window_state == 1:
        window_save = True
    else:
        window_save = False

def play_clicking_sound():
    sound = pygame.mixer.Sound('audio/click.mp3')
    sound.play()

def toggle_clicking_sounds():
    global sound_enabled
    sound_state = sound.get()
    if sound_state == 1:
        sound_enabled = True
    else:
        sound_enabled = False

def toggle_labels():
    global d2c, v2c
    labels_state = labels.get()
    if labels_state == 1:
        d2c.grid_forget()
        v2c.grid_forget()
    else:
        d2c.grid(row=4, column=2, pady=(5, 0), padx=(5, 5), sticky='w')
        v2c.grid(row=5, column=2, pady=(5, 0), padx=(5, 5), sticky='w')
        
def toggle_theme():
    theme_state = theme.get()
    if theme_state == 1:
        customtkinter.set_appearance_mode('Light')
    else:
        customtkinter.set_appearance_mode('Dark')

def repeat_until_stopped_toggle():
    global repeat_until_stopped_enabled
    repeat_until_stopped_state = repeat_until_stopped.get()
    if repeat_until_stopped_state == 1:
        repeat_until_stopped_enabled = True
        save_settings()
    else:
        repeat_until_stopped_enabled = False
        save_settings()

# def on_window_resize(event):
    # global window_width, window_height
    # window_width = event.width
    # window_height = event.height
    # save_settings()

load_settings()

root.bind_all('<1>', lambda event: event.widget.focus_set())

keyboard.hook_key(hotkey, hotkey_autoclicker)

lp = CTkFrame(root)
lp.grid(row=1, column=0, sticky='nsew')

lpb1 = CTkButton(lp, text='Menu', command=toggle_menu)
lpb1.grid(row=0, column=0, pady=(10, 0), sticky='ew')

lpb2 = CTkButton(lp, text='Reset', command=reset_to_default_settings)
lpb2.grid(row=1, column=0, pady=(10, 0), sticky='ew')

lpb3 = CTkButton(lp, text='Info', command=display_info)
lpb3.grid(row=2, column=0, pady=(10, 0), sticky='ew')

lp2 = CTkFrame(root)

t2 = CTkLabel(lp2, text=('Hotkey: ' + hotkey.upper()))
t2.grid(row=0, column=0, columnspan=2, pady=(9, 0), sticky='w')

b1 = CTkButton(lp2, text='Change Hotkey', command=hotkey_record)
b1.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky='ew')

b2 = CTkButton(lp2, text='Start', command=turn_on_autoclicker)
b2.grid(row=2, column=0, pady=(5, 0), sticky='ew')

b3 = CTkButton(lp2, text='Stop', command=turn_off_autoclicker)
b3.grid(row=2, column=1, pady=(5, 0), sticky='ew')

d1 = CTkLabel(lp2, text='Mouse Click Type:')
d1.grid(row=3, column=0, pady=(5, 0), sticky='w')

d1m = CTkOptionMenu(master=lp2, values=mouse_button_options, command=change_mouse_button, variable=selected_mouse_button_var)
d1m.grid(row=3, column=1, pady=(5, 0), sticky='ew')

d2 = CTkLabel(lp2, text='Click Type:')
d2.grid(row=4, column=0, pady=(5, 0), sticky='w')

d2m = CTkOptionMenu(master=lp2, values=click_type_options, command=change_click_type, variable=selected_click_type_var)
d2m.grid(row=4, column=1, pady=(5, 0), sticky='ew')

d2c = CTkLabel(lp2, text='Your CPS will depend on click type', font=('', 10))
d2c.grid(row=4, column=2, pady=(5, 0), padx=(5, 5), sticky='w')

v1 = CTkLabel(lp2, text='CPS: (clicks per second)')
v1.grid(row=5, column=0, pady=(5, 0), sticky='w')

v2 = CTkEntry(lp2)
v2.insert(0, str(cps))
v2.grid(row=5, column=1, pady=(5, 0), sticky='ew')

v2c = CTkLabel(lp2, text='Max CPS is 2,000', font=('', 10))
v2c.grid(row=5, column=2, pady=(5, 0), padx=(5, 5), sticky='w')

v3 = CTkButton(lp2, text='Set CPS', command=set_cps)
v3.grid(row=7, column=0, columnspan=2, pady=(5, 0), sticky='ew')

r1 = CTkLabel(lp2, text='Repeat: (repeat CPS)')
r1.grid(row=8, column=0, pady=(5, 0), sticky='w')

r2 = CTkEntry(lp2)
r2.insert(0, str(repeat))
r2.grid(row=8, column=1, pady=(5, 0), sticky='ew')

r3 = CTkButton(lp2, text='Set Repeat', command=set_repeat)
r3.grid(row=9, column=0, columnspan=2, pady=(5, 0), sticky='ew')

repeat_until_stopped = CTkCheckBox(lp2, text='Repeat until stopped', variable=repeat_until_stopped, command=repeat_until_stopped_toggle)
repeat_until_stopped.grid(row=8, column=2, columnspan=2, pady=(5, 0), padx=(5, 5), sticky='w')

esc = CTkCheckBox(lp2, text='ESC to stop autoclicking', variable=esc, command=toggle_esc)
esc.grid(row=10, column=0, columnspan=2, pady=(5, 0), sticky='w')

show = CTkCheckBox(lp2, text='Show autoclicker over all other windows', variable=show, command=toggle_show)
show.grid(row=11, column=0, columnspan=2, pady=(5, 0), sticky='w')

window = CTkCheckBox(lp2, text='Save window height and width on exit', variable=window, command=toggle_window_saving_width_height_on_exit)
window.grid(row=12, column=0, columnspan=2, pady=(5, 0), sticky='w')

sound = CTkCheckBox(lp2, text='Toggle clicking sounds', variable=sound, command=toggle_clicking_sounds)
sound.grid(row=13, column=0, columnspan=2, pady=(5, 0), sticky='w')

labels = CTkCheckBox(lp2, text='Hide text labels at right of autoclicker', variable=labels, command=toggle_labels)
labels.grid(row=14, column=0, columnspan=2, pady=(5, 0), sticky='w')

theme = CTkCheckBox(lp2, text='Light theme', variable=theme, command=toggle_theme)
theme.grid(row=15, column=0, columnspan=2, pady=(5, 0), sticky='w')

t3 = CTkLabel(lp, text=('v' + str(version)))
t3.grid(row=9, column=0, columnspan=2, pady=(5, 0), sticky='ew')

root.geometry(f"{window_width}x{window_height}")

root.protocol('WM_DELETE_WINDOW', closing)

root.mainloop()
