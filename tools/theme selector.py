import os
import json

'''
CUSTOM VERSION OF PICK WITH CUSTOM MODIFICATIONS

Modifications: 
    * Excluded indexes

'''

import curses
from dataclasses import dataclass, field
from typing import Any, List, Optional, Sequence, Tuple, TypeVar, Union, Generic

__all__ = ["Picker", "pick", "Option"]


@dataclass
class Option:
    label: str
    value: Any


KEYS_ENTER = (curses.KEY_ENTER, ord("\n"), ord("\r"))
KEYS_UP = (curses.KEY_UP, ord("k"))
KEYS_DOWN = (curses.KEY_DOWN, ord("j"))
KEYS_SELECT = (curses.KEY_RIGHT, ord(" "))

SYMBOL_CIRCLE_FILLED = "(x)"
SYMBOL_CIRCLE_EMPTY = "( )"

OPTION_T = TypeVar("OPTION_T", str, Option)
PICK_RETURN_T = Tuple[OPTION_T, int]


@dataclass
class Picker(Generic[OPTION_T]):
    options: Sequence[OPTION_T]
    title: Optional[str] = None
    indicator: str = "*"
    default_index: int = 0
    multiselect: bool = False
    min_selection_count: int = 0
    selected_indexes: List[int] = field(init=False, default_factory=list)
    excluded_indexes: List[int] = field(default_factory=list)
    index: int = field(init=False, default=0)
    screen: Optional["curses._CursesWindow"] = None

    def __post_init__(self) -> None:
        if len(self.options) == 0:
            raise ValueError("options should not be an empty list")

        if self.default_index >= len(self.options):
            raise ValueError("default_index should be less than the length of options")

        if self.multiselect and self.min_selection_count > len(self.options):
            raise ValueError(
                "min_selection_count is bigger than the available options, you will not be able to make any selection"
            )

        self.index = self.default_index
        while self.index in self.excluded_indexes:
            self.index += 1

    def move_up(self) -> None:
        self.index -= 1

        while self.index in self.excluded_indexes:
            self.index -= 1
        if self.index < 0:
            self.index = len(self.options) - 1

    def move_down(self) -> None:
        self.index += 1

        while self.index in self.excluded_indexes:
            self.index += 1
        if self.index >= len(self.options):
            self.index = 0

    def mark_index(self) -> None:
        if self.multiselect:
            if self.index in self.selected_indexes:
                self.selected_indexes.remove(self.index)
            else:
                self.selected_indexes.append(self.index)

    def get_selected(self) -> Union[List[PICK_RETURN_T], PICK_RETURN_T]:
        """return the current selected option as a tuple: (option, index)
        or as a list of tuples (in case multiselect==True)
        """
        if self.multiselect:
            return_tuples = []
            for selected in self.selected_indexes:
                return_tuples.append((self.options[selected], selected))
            return return_tuples
        else:
            return self.options[self.index], self.index

    def get_title_lines(self) -> List[str]:
        if self.title:
            return self.title.split("\n") + [""]
        return []

    def get_option_lines(self) -> List[str]:
        lines: List[str] = []
        for index, option in enumerate(self.options):
            if index == self.index:
                prefix = self.indicator
            else:
                prefix = len(self.indicator) * " "

            if self.multiselect:
                symbol = (
                    SYMBOL_CIRCLE_FILLED
                    if index in self.selected_indexes
                    else SYMBOL_CIRCLE_EMPTY
                )
                prefix = f"{prefix} {symbol}"

            option_as_str = option.label if isinstance(option, Option) else option
            lines.append(f"{prefix} {option_as_str}")

        return lines

    def get_lines(self) -> Tuple[List, int]:
        title_lines = self.get_title_lines()
        option_lines = self.get_option_lines()
        lines = title_lines + option_lines
        current_line = self.index + len(title_lines) + 1
        return lines, current_line

    def draw(self, screen: "curses._CursesWindow") -> None:
        """draw the curses ui on the screen, handle scroll if needed"""
        screen.clear()

        x, y = 1, 1  # start point
        max_y, max_x = screen.getmaxyx()
        max_rows = max_y - y  # the max rows we can draw

        lines, current_line = self.get_lines()

        # calculate how many lines we should scroll, relative to the top
        scroll_top = 0
        if current_line > max_rows:
            scroll_top = current_line - max_rows

        lines_to_draw = lines[scroll_top: scroll_top + max_rows]

        for line in lines_to_draw:
            screen.addnstr(y, x, line, max_x - 2)
            y += 1

        screen.refresh()

    def run_loop(
        self, screen: "curses._CursesWindow"
    ) -> Union[List[PICK_RETURN_T], PICK_RETURN_T]:
        while True:
            self.draw(screen)
            c = screen.getch()
            if c in KEYS_UP:
                self.move_up()
            elif c in KEYS_DOWN:
                self.move_down()
            elif c in KEYS_ENTER:
                if (
                    self.multiselect
                    and len(self.selected_indexes) < self.min_selection_count
                ):
                    continue
                return self.get_selected()
            elif c in KEYS_SELECT and self.multiselect:
                self.mark_index()

    def config_curses(self) -> None:
        try:
            # use the default colors of the terminal
            curses.use_default_colors()
            # hide the cursor
            curses.curs_set(0)
        except:
            # Curses failed to initialize color support, eg. when TERM=vt100
            curses.initscr()

    def _start(self, screen: "curses._CursesWindow"):
        self.config_curses()
        return self.run_loop(screen)

    def start(self):
        if self.screen:
            # Given an existing screen
            # don't make any lasting changes
            last_cur = curses.curs_set(0)
            ret = self.run_loop(self.screen)
            if last_cur:
                curses.curs_set(last_cur)
            return ret
        return curses.wrapper(self._start)


def pick(
    options: Sequence[OPTION_T],
    title: Optional[str] = None,
    indicator: str = "*",
    default_index: int = 0,
    multiselect: bool = False,
    min_selection_count: int = 0,
    excluded_indexes = list,
    screen: Optional["curses._CursesWindow"] = None,
):
    picker: Picker = Picker(
        options,
        title,
        indicator,
        default_index,
        multiselect,
        min_selection_count,
        excluded_indexes,
        screen,
    )
    return picker.start()


'''
Theme selector code 
'''

themes_dir = os.path.abspath("../themes")

def get_file_tree(path, excluded=None):
    if excluded is None:
        excluded = []
    tree = []

    for file in os.listdir(path):
        if file in excluded:
            continue

        if os.path.isdir(path+"/"+file):
            tree.append({file: get_file_tree(path+"/"+file, excluded=excluded)})
        else: tree.append(file)

    return tree


def beautify_tree(tree, indentation_level=0, tree_list=None, path=""):
    out = ""
    indents = '   '*indentation_level
    if tree_list is None: tree_list = []
    for file in tree:
        if type(file) == dict:
            out += f"{indents}└──{list(file)[0]}\n"
            tree_list.append(path+list(file)[0])
            out += beautify_tree(file[list(file)[0]], indentation_level+1, tree_list, f"{path}/{list(file)[0]}")[0]
        else:
            tree_list.append(f"{path}/{file}")
            out += f"{indents}└──{file}\n"

    return out, tree_list


def remove_themes(tree):
    out = []
    for file in tree:
        if type(file) == dict:
            newtree = file[list(file)[0]]
            if "config.json" not in newtree:
                out.append({list(file)[0]: remove_themes(newtree)})
            else: out.append(list(file)[0])
        else: out.append(file)
    return out


def get_excluded_indexes(tree):  # Only accepts the list with the beautified tree
    excluded = []

    for idx, item in enumerate(tree):
        count = item.count("   ")
        try: next_count = tree[idx+1].count("   ")
        except IndexError: next_count = count

        if count >= next_count:
            continue
        excluded.append(idx)

    return excluded

tree, tree_list = beautify_tree(remove_themes(get_file_tree(themes_dir, excluded=["required", "__pycache__"])))
excluded = get_excluded_indexes(tree.splitlines())
theme = pick(tree.splitlines(), "Please select the theme you want to select.", excluded_indexes=excluded, indicator=">>")[1]

with open("../config.json", "r") as f:
    config = json.load(f)

config["current theme"] = tree_list[theme]
with open("../config.json", "w") as f:
    json.dump(config, f, indent=4)

print("Successfully selected your current theme")
os.system("pause")