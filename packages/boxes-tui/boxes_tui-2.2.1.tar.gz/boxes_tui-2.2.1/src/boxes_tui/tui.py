#####       boxes.py       #####
# 
# Boxes is a collection of python TUI tools
# 
#####      made by L7      #####

# Copyright (c) 2025
# Legende_7  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER OR CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY 
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, 
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE 
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import curses

class TUI:
    #############
    ### BOXES ###
    #############
    @staticmethod
    def box(window, size,coords, top:str,side:str, tl:str,tr:str=None,bl:str=None,br:str=None):
        ### CORNER DEFAULTS ###
        if tr == None:
            tr = tl
        if bl == None:
            bl = tl
        if br == None:
            br = tl
        ### DRAW THE BOX ###
        window.addstr(coords[1], coords[0], f"{tl}" + f"{top}" * (size[0] - 2) + f"{tr}")
        window.addstr(coords[1] + size[1] - 1, coords[0], f"{bl}" + f"{top}" * (size[0] - 2) + f"{br}")
        for i in range(1, size[1] - 1):
            window.addstr(coords[1] + i, 0, f"{side}")
            window.addstr(coords[1] + i, coords[0] + size[0] - 1, f"{side}")

    def make_window(x, y, width, height):
        new_window = curses.newwin(height, width, y, x)
        new_window.keypad(True)
        return new_window

    def display_text(self, window, x: int, y: int, text: str, curses_options = 0):
        text_parts = text.split("§//")
        texts = []
        colours = [0]
        for z in text_parts:
            texts.append(z.split("//§")[0])
            if len(z.split("//§")) == 1:
                colours.append(0)
            else:
                colours.append(int(z.split("//§")[1]))

        try:
            x_offset = 0
            i = 0
            while i < len(texts):
                window.addstr(y, int(x) + x_offset, texts[i], curses.color_pair(colours[i]) | curses_options)
                x_offset += len(texts[i])
                i += 1
            return 0
        except:
            return 1

    def colour_pair(i: int, foreground, background):
        curses.init_pair(i, foreground, background)

    class button:
        def tick(self):
            pass
        def __init__(self):
            pass



    ##################
    ### MENU LOGIC ###
    ##################
    
    ### Helper functions ###
    def nothing(self):
        return None
    class Menu:
        ### SELECTIONS & STUFF ###
        def move_up(self):
            if self.selected_option - 1 >= 0:
                self.selected_option -= 1
                if self.selected_option <= 0 + self.scroll - 1:
                    self.scroll -= 1

        def move_down(self):
            if self.selected_option + 1 <= len(self.contents) - 1:
                self.selected_option += 1
                if self.selected_option > self.height + self.scroll:
                    self.scroll += 1
        
        def select(self):
            return True, self.selected_option, self.contents[self.selected_option][1]()

        def back(self):
            if self.allow_back:
                return True, -(self.selected_option +  1), None   
                
        def default_keybinds(self):
            return [
                ([curses.KEY_UP], self.move_up),
                ([curses.KEY_DOWN], self.move_down),
                ([10, curses.KEY_RIGHT], self.select),
                ([curses.KEY_BACKSPACE, curses.KEY_LEFT], self.back)
            ]

        def display_entry(self, entry_label: str, y: int):
            ### OPTIONS ###
            if y == self.selected_option:
                entry_options = self.curses_options | curses.A_REVERSE
            else:
                entry_options = self.curses_options

            text_parts = entry_label.split("§//")
            texts = []
            colours = [0]
            for x in text_parts:
                texts.append(x.split("//§")[0])
                if len(x.split("//§")) == 1:
                    colours.append(0)
                else:
                    colours.append(int(x.split("//§")[1]))

            ### DISPLAY ###
            try:
                x = 0
                i = 0
                while i < len(texts):
                    self.menu_pad.addstr(y, x, texts[i], curses.color_pair(colours[i]) | entry_options)
                    x += len(texts[i])
                    i += 1
                return 0
            except:
                return 1

        def tick(self, keypress):
            ### PROCCESS KEYPRESSES ###
            return_value = (False, self.selected_option, None)
            for x in self.keybinds:
                if keypress in x[0]:
                    return_value = x[1]()
            ### UPDATE SELECTED OPTION ###
            if self.selected_option >= len(self.contents):
                self.selected_option = 0
            self.height, self.width = self.menu_win.getmaxyx()

            ### DISPLAY MENU ###
            if self.full_refresh:                                  # Refresh everything
                self.menu_pad.clear()
                y = 0
                for menu_content in self.contents:
                    self.display_entry(menu_content[0], y)
                    y += 1
            elif self.selected_option != self.old_selected_option: # Refresh only the selected and old selected option
                self.display_entry(self.contents[self.old_selected_option][0], self.old_selected_option)
                self.display_entry(self.contents[self.selected_option][0], self.selected_option)
            
            try:
                self.menu_pad.refresh(self.scroll,0, self.menu_win.getbegyx()[0],self.menu_win.getbegyx()[1], self.height,self.width)
            except:
                pass

            return return_value

        # Contents must be fed into like this:
        # [(name, funtion to call)]
        def __init__(self, menu_win, contents, allow_back: bool = False, keybinds = None):
            ### WIN / PAD SETUP ###
            self.menu_win = menu_win
            self.height, self.width = menu_win.getmaxyx()
            self.pad_height = len(contents)
            self.pad_width = max(max(len(x[0]) for x in contents), self.width)
            self.menu_pad = curses.newpad(self.pad_height, self.pad_width)

            ### MENU SETTINGS SETUP ###
            if keybinds is None: self.keybinds = self.default_keybinds()
            else: self.keybinds = keybinds
            self.mouse = False
            self.bold = False
            self.allow_back = allow_back

            ### INTERNAL VARS ###
            self.contents = contents
            self.full_refresh = True
            self.selected_option = 0
            self.old_selected_option = 0
            self.scroll = 0

            if self.bold: self.curses_options = curses.A_BOLD
            else: self.curses_options = 0

            self.tick(None)

    ##################
    ### INIT LOGIC ###
    ##################
    def __init__(self, default_colors: bool = True, stdscr = None):
        ### TERM ###
        if stdscr is None: # No wrapper
            self.stdscr = curses.initscr()
            self.call_endwin = True
        else:              # Wrapper
            self.stdscr = stdscr
            self.call_endwin = False
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(True)

        ### COLOURS ###
        curses.start_color()
        self.init_colours(default_colors)

    def init_colours(self, default_colors: bool):
        if default_colors:
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_RED, -1)
            curses.init_pair(2, curses.COLOR_GREEN, -1)
            curses.init_pair(3, curses.COLOR_BLUE, -1)
            curses.init_pair(4, curses.COLOR_YELLOW, -1)
            curses.init_pair(5, curses.COLOR_MAGENTA, -1)
            curses.init_pair(6, curses.COLOR_CYAN, -1)
        else:
            #curses.init_pair(0, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
            curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)

    def cleanup(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        if self.call_endwin:
            curses.endwin()