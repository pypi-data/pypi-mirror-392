import matplotlib as mpl

# print("Default font family:", mpl.rcParams['font.family'])
# print("Fonts under sans-serif:", mpl.rcParams['font.sans-serif'])
# print(mpl.font_manager.get_font_names())
mpl.rcParams['font.family'] = 'serif'
print(mpl.rcParams['font.sans-serif'])
# ['DejaVu Sans', 'Bitstream Vera Sans', 'Computer Modern Sans Serif', 'Lucida Grande', 'Verdana', 'Geneva', 'Lucid', 'Arial', 'Helvetica', 'Avant Garde', 'sans-serif']