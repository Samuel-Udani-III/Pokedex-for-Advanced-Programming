import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk
from PIL import Image

# Get our pokedex - the "name" column contains the names of all Pokemon so far
pokedex = pd.read_csv("Full Pokedex Cleaned v2.csv", index_col = 0)

# A list of stats - we'll use this later.
stats = ['hp', 'attack', 'defence', 'sp_attack', 'sp_defence', 'speed']

def scale_stat(x):
    """
    Scales a stat to a specific range. 
    
    In this case, 1 and 250 describe the minimum and maximum width of the bar in pixels.
    
    The stat will thus be scaled to return a width (in pixels) relative to the maximum and 
    minimum values of all stats.
    
    This returns start_x2 in pixels.
    """
    start_x1 = 250
    start_x2 = 1
    
    # The minimum value of any stat
    min_x = 20
    # The reasonable maximum value of any stat (there are several outliers)
    max_x = 150
    
    if x < min_x:
        x = min_x
    elif x > max_x:
        x = max_x
        
    return round((start_x1 - start_x2)*((x - min_x) / (max_x - min_x)) + start_x2)

def select_pokemon(move = None):
    '''
    When run, the app should update all fields with the appropriate values based on the 
    pokedex above.
    
    Note that this function is specifically designed for the dataframe generated
    from the .csv file loaded above - your function may be different depending on
    your data source.
    '''
       
    # If we pressed the right (forward) or left (backward) buttons, 
    # we want to change Pokemon.
    try:
        if move == 'forward':
            # Move the current selection forward by one item.
            search_box.current(search_box.current() + 1)
            # Get the name of the Pokemon in the search_box
            selected = search_box.get()
        elif move == 'backward':
            # Move the current selection forward by one item.
            search_box.current(search_box.current() - 1)
            selected = search_box.get()
        else:
            selected = search_box.get()
    # If there's an error (generally related to pressing forward on the last pokemon
    # or backward on the first pokemon), we'll just get the current Pokemon
    except Exception as e:
        # Print the error to see what went wrong
        print(e)
        selected = search_box.get()
    
    
    ##### Fill in text-based information #####
    
    # The name of the Pokemon
    # note that we split the name of the Pokemon to a new line if its too long
    name_label["text"] = "\n".join(selected.split(" - "))
    
    # The Pokedex entry
    pokedex_entry_string = ". ".join(pokedex[pokedex.name == \
                              selected]["pokedex_entry"].values[0].split(". ")[:4])
    
    # Add the period to the end of the sentence if there isn't one.
    if pokedex_entry_string[-1] != "." and pokedex_entry_string[-1] != "!":
        pokedex_entry_string += "."
    
    pokedex_entry["text"] = pokedex_entry_string
    
    # The height and weight in real units
    height_entry["text"] = "Height:\n" + str(pokedex[pokedex.name == \
                                             selected]["height"].values[0]) + " m"
    weight_entry["text"] = "Weight:\n" + str(pokedex[pokedex.name == \
                                             selected]["weight"].values[0]) + " kg"

    # The catch rate
    # Note that there are no "catch rates" for Pokemon Arceus - these are recorded as 
    # N/A in my database
    if pokedex[pokedex.name == selected]["catch_rate"].isna().all():
        catch_entry["text"] = "Catch Rate:\nNo known data"
    else:
        catch_entry["text"] = "Catch Rate:\n" + str(pokedex[pokedex.name == \
                                                selected]["catch_rate"].values[0]) \
                                                + "%\nwith Pokeball"
    
    ##### Fill in Picture-based information #####
    
    # Display the Pokemon's image
    label_image = ImageTk.PhotoImage(file = \
                 f"Pokemon Pictures/{pokedex[pokedex.name == selected].index[0] + 1}.png")
    pic_label.config(image = label_image)
    # Remember to keep a reference to the image or it won't display!
    pic_label.image = label_image
    
    # Get and display the appropriate image for the pokemon's type
    type1label["image"] = type_dict[pokedex[pokedex.name == selected]["type1"].values[0]]
    
    # Note that many Pokemon have a "null" second typing. In such cases, we turn off the type2label
    # using grid_forget
    if pokedex[pokedex.name == selected]["type2"].values[0] == "none":
        type2label.grid_forget()
    else:
        type2label["image"] = type_dict[pokedex[pokedex.name == selected]["type2"].values[0]]
        type2label.grid(row = 0, column = 1)
        
    ##### Fill in Stats #####
    
    # Delete all existing bars in the canvas
    for widget in stat_frame.winfo_children():
        widget.destroy()
    
    # Recreate the Canvas - a Canvas is basically an area where we can draw simple shapes
    draw_box = tk.Canvas(stat_frame, height = 100, width = 275, bg = "white", 
                     borderwidth = 0, highlightthickness = 0)
    draw_box.grid(row = 0, rowspan = 6, column = 2, sticky = "nsew")
    
    # These are values that I have determined using trial and error to get the best looking
    # bars. These values describe the coordinates of the top left and bottom right corners of
    # the bar I want to draw. 
    start_x1 = 0
    start_y1 = 7
    start_x2 = 250
    start_y2 = 27
    bar_height = 20 # height of each stat bar
    bar_step = 13 # distance between bars

    for row, stat in enumerate(stat_block):
        # Get the value of the stat
        stat_value = pokedex[pokedex.name == selected][stats[row]].values[0]
        
        # Recreate the text box containing the appropriate value
        text_box = tk.Label(stat_frame, 
                            # Add the value of the appropriate stat
                            text = stat + f" {stat_value}",
                            font = ("Futura", 12),
                            anchor = "w",
                            bg = "white",
                            justify = tk.LEFT,
                            borderwidth = 0)
        text_box.grid(row = row, column = 0, sticky = "nsw")
        
        # Higher stats should be green, lower stats should be red.
        if stat_value <= 50:
            fill = "red"
        elif 51 <= stat_value < 70:
            fill = "orange"
        elif 70 <= stat_value < 90:
            fill = "yellow"
        else:
            fill = "green"
        
        # Draw a bar of the appropriate length
        draw_box.create_rectangle(start_x1, 
                                  start_y1, 
                                  # Scale the bar so that it has the correct length relative
                                  # to the value of the stat
                                  scale_stat(stat_value),
                                  start_y2, 
                                  fill = fill)
        
        # Increment the value of y1 and y2 so that the next bar is shifted downwards
        # and has the appropriate "thickness"
        start_y1 = start_y2 + bar_step
        start_y2 = start_y1 + bar_height
    # The window!
window = tk.Tk()

window.title("Pokedex")
window.geometry("1200x700")
window.configure(background = "crimson")

# A list of all the Pokemon types. 
type_list = ['grass', 'fire', 'water', 'bug', 'normal', 'dark', 'poison',
       'electric', 'ground', 'ice', 'fairy', 'steel', 'fighting',
       'psychic', 'rock', 'ghost', 'dragon', 'flying']
# We have separate pictures for each Pokemon type, so we'll put them into a dictionary
# so that they won't get lost!
type_dict = {i: ImageTk.PhotoImage(file = f"Type Pictures/{i.capitalize()}.png") for i in type_list}

# # Note that many Pokemon have a "null" second typing. If you want to, 
# you can include it in the dictionary and have the label be displayed as a empty value
# This is kind of okay, but you can see still see an empty label if you look closely.
# type_dict['none'] = ''

# # No longer needed
# # A StringVar is a variable that can be linked to a widget. If assigned to textvariable,
# # whenever the text value of that widget changes, StringVar will change as well.
# selected = tk.StringVar()

# Configure 4 rows and 3 columns.
window.rowconfigure(0, weight = 0, pad = 20)
window.rowconfigure([i for i in range(1,4)], weight = 1)
window.columnconfigure([i for i in range(3)], minsize = 50, weight = 1)

### Name Frame
name_frame = tk.Frame(window, relief = tk.RAISED, borderwidth = 4, bg = "blue1")
name_label = tk.Label(name_frame, 
                      height = 2,
                      text = "Pokemon Name Here", 
                      fg = "yellow",
                      bg = "blue1",
                      font = ("Futura", 16, "bold"))
# One of the few cases where you can mix pack() with grid().
name_label.pack()
name_frame.grid(row = 0, column = 0, padx = 10, sticky = "ew")

### Picture Frame
picture_frame = tk.Frame(window, 
                         relief = tk.SUNKEN, 
                         borderwidth = 2, 
                         height = 400,
                         width = 400,
                         bg = "white")

picture_frame.rowconfigure(0, weight = 1)
picture_frame.columnconfigure(0, weight = 1)

pic_label = tk.Label(picture_frame, bg = "white")
pic_label.grid(row = 0, column = 0, sticky = "nsew")

picture_frame.grid(row = 1, column = 0, rowspan = 2, sticky = "nsew", padx = 10)
picture_frame.grid_propagate(False)

### Type Frame
type_frame = tk.Frame(window, relief = tk.RAISED, borderwidth = 2)
type1label = tk.Label(type_frame, text = "Type 1 Here", font = ("Futura", 16))
type1label.grid(row = 0, column = 0)
type2label = tk.Label(type_frame, text = "Type 2 Here", font = ("Futura", 16))
type2label.grid(row = 0, column = 1)
type_frame.grid(row = 3, column = 0)


### Info Frame
info_frame = tk.Frame(window, relief = tk.SUNKEN, borderwidth = 4)

# Calling rowconfigure and columnfigure within the info_frame
# causes the contents of the frame (label) to be centered within it.
info_frame.rowconfigure([0,1,2], weight = 2, minsize = 200)
# info_frame.rowconfigure([1,2], weight = 1, minsize = 80)
info_frame.columnconfigure([0,1], weight = 1, minsize = 300)


## Various Information

# The Pokedex entry is long, so we'll let it take up two columns
# Use wraplength to tell the app to wrap text in this label.
pokedex_entry = tk.Label(info_frame, text = "Pokedex Entry", font = ("Futura", 16),
                         wraplength = 700, anchor = "w", bg = "black", fg = "light blue",
                         justify=tk.LEFT)
pokedex_entry.grid(row = 0, column = 0, columnspan = 2, sticky = "nsew")

height_entry = tk.Label(info_frame, text = "Height", font = ("Futura", 16), borderwidth = 2,
                       relief = tk.RIDGE, bg = "white")
height_entry.grid(row = 1, column = 0, sticky = "nsew")

weight_entry = tk.Label(info_frame, text = "Weight", font = ("Futura", 16), borderwidth = 2,
                       relief = tk.RIDGE, bg = "white")
weight_entry.grid(row = 1, column = 1, sticky = "nsew")

catch_entry = tk.Label(info_frame, text = "Catch Rate", font = ("Futura", 16), borderwidth = 2,
                      relief = tk.RIDGE, bg = "white")
catch_entry.grid(row = 2, column = 1, sticky = "nsew")

# Create a special frame for the stats
stat_frame = tk.Frame(info_frame, borderwidth = 2, relief = tk.RIDGE, bg = "white")

stat_frame.rowconfigure([i for i in range(6)], weight = 1)
stat_frame.columnconfigure(1, weight = 1)

stat_block = ["HP:", "ATK:", "DEF:", "SPA:", "SPD:", "SPE:"]

draw_box = tk.Canvas(stat_frame, height = 100, width = 275, bg = "white", 
                     borderwidth = 0, highlightthickness = 0)

draw_box.grid(row = 0, rowspan = 6, column = 2, sticky = "nsew")

# These values were selected by trial and error - see select_pokemon()
start_x1 = 0
start_y1 = 7
start_x2 = 250
start_y2 = 27
bar_height = 20 # height of each stat bar
bar_step = 13 # distance between bars

for row, stat in enumerate(stat_block):
    text_box = tk.Label(stat_frame, 
                        text = stat,
                        font = ("Futura", 12),
                        anchor = "w",
                        bg = "white",
                        justify = tk.LEFT,
                        borderwidth = 0)
    text_box.grid(row = row, column = 0, sticky = "nsw")

    draw_box.create_rectangle(start_x1, start_y1, start_x2, start_y2, fill = "green")
    
    start_y1 = start_y2 + bar_step
    start_y2 = start_y1 + bar_height
    
# draw_box.pack(side = tk.LEFT)
stat_frame.grid(row = 2, column = 0, sticky = "nsew")

info_frame.grid(row = 1, rowspan = 3, column = 1, columnspan = 2, sticky = "nsew")
# Grid propagate tells the app not to resize the frame - doesn't always work!
info_frame.grid_propagate(False)

### Search Frame
search_frame = tk.Frame(window, relief = tk.RAISED, borderwidth = 3, bg = "light blue")

# Calling rowconfigure and columnfigure within the info_frame
# causes the contents of the frame (label) to be centered within it.
search_frame.columnconfigure([0,1,2,3,4], weight = 1)
search_frame.rowconfigure(0, weight = 1, minsize = 55)

# Turn the buttons into actual buttons
left_button = tk.Button(search_frame, text = "Previous", font = ("Futura", 16), 
                        command = lambda: select_pokemon(move = "backward"))
left_button.grid(row = 0, column = 0, sticky = "ew")

submit_button = tk.Button(search_frame, text = "Search!", font = ("Futura", 14), 
                          command = select_pokemon)
submit_button.grid(row = 0, column = 3)

right_button = tk.Button(search_frame, text = "  Next  ", font = ("Futura", 16),
                         command = lambda: select_pokemon(move = "forward"))
right_button.grid(row = 0, column = 4, sticky = "ew")


def search_pokemon():
    """
    This function runs with every keystroke made in the search box
    
    It will filter the list of Pokemon such that all remaining options match the string
    in the search box
    """
    current_text = search_box.get()
    if current_text == "" or current_text in pokedex.name.tolist():
        search_box.config(values = pokedex.name.tolist())
    else:
        values = []
        for name in pokedex.name.tolist():
            if current_text.lower() in name.lower():
                values.append(name)
        search_box.config(values = values)
    
        
# Adjust to make a combobox
# Needs a values argument that requires a list of Pokemon
search_box = ttk.Combobox(search_frame, 
                          values = pokedex.name.tolist(),
                          font = ("Futura", 16), 
                          postcommand = search_pokemon)
search_box.grid(row = 0, column = 1, columnspan = 2, sticky = "nsew", pady = 5, padx = 10)

search_frame.grid(row = 0, column = 1, columnspan = 2, sticky = "ew")


# Run the App
window.mainloop()