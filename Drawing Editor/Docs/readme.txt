## Run code
- run python3 filename(DigiDraw) on terminal.
- the drawing editor will automatically pop up.

## Drawing object
- you can draw a line or rectangle from options given below by just clicking on them and movin cursor to white space given in drawing editor to draw the object

## Editing
- you have options to delete,rotate,copy,move,resize and edit(changing outline colour).
- for that you need to select the object that you want to edit
- then you need to go onto edit menu and click on whatever operation you want to perform.

### delete
- you need to click on the delete option in order to delete the object you have selected.

### rotate
- you need to go to the rotate option ,a dialog box will appear there you need to enter the degree with which you want to rotate the object selected.

### resize
- you need to got to resize option, a dialog will appear there you need to enter length and width in order to change the size of the object.

### edit(change outline colour)
- you need to go to edit menu and there you need to select edit option, a dialog box will apppear.
- there you need to choose  the variant of colour you want for your selected object.

### move
- you need to select the move option in the edit option
- Then you need to click on the object and drag
- Then click on the object again and your move operation will be done.

## Save
- you can save as well as export from various formats

### Save as Jpeg
- you can need to select the option , you need to enter the filename with which you want to save the it.

### Save as txt
- you can save as txt and same opertaion as mentioned above in case of save as Jpeg

### Export from Jpeg
- you can open any jpeg format file through this option ,you just need to enter filename

### Export as XML
- you can export any file in xml format ,you need to enter the filename with which you want to save it.

### open
- you can open files saved in txt or xml format.You just need to enter the fileaname in the dialog box.

## Group
### select for grouping
- you need to first select this option in group menu in order to group
- then you need to select the object you want to group.

### Group
- you need to select this option after selecting the object.
- after selecting this option your object will be grouped.

### Ungroup
- you need to first select the group which you want to Ungroup
- then you need to select this ungroup option in order to ungroup object

### Ungroup_all
- you need to select this option in order to ungroup all groups formed.
- In this you donot need to select any object.


***Assumptions***

1)The Canvas board is set to 400x400 size as instructed.

2)Rounded rectangles are converted to polygon and the points required to make that polygon(greater than 4 unlike in case of rectangle) is stored for saving/opening.

3)Rotate(an extended functionality) is implimented on a single object currently but can be extended to work with groups too in future(extendable).

4)On moving a single item in a group it will get displaced but will still remain a part of that group. Now moving the group will keep the elemets of that groups in relatively same distance.