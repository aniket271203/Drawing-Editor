
---

## Drawing Editor

A powerful yet simple drawing editor that allows users to create, edit, and save drawings with ease. This project demonstrates basic and advanced drawing capabilities, making it perfect for those looking to explore graphical user interface development.

### Features

- **Basic Drawing Tools**: Draw lines and rectangles with a simple click and drag interface.
- **Editing Options**: Delete, rotate, copy, move, resize, and change the outline color of your objects.
- **Group/Ungroup Objects**: Easily group multiple objects for collective manipulation or ungroup them.
- **Save and Export**: Save your work in various formats such as JPEG, TXT, and XML.
- **Open Files**: Open previously saved files in TXT or XML format.

### Getting Started

#### Prerequisites

- Python 3.x

#### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/drawing-editor.git
    ```
2. Navigate to the project directory:
    ```sh
    cd drawing-editor
    ```

#### Running the Application

Run the following command in your terminal:
```sh
python3 filename.py file.txt
```
The drawing editor will automatically pop up.If you pass a text file that has a format of the saved files from my app then you can open an existing drawing.

### Usage

#### Drawing Objects

- **Draw Line or Rectangle**: Select the desired shape from the options and draw it on the white canvas by clicking and moving the cursor.

#### Editing Objects

1. **Select Object**: Click on the object you wish to edit.
2. **Edit Menu**: Choose from the following editing options:

    - **Delete**: Click the delete option to remove the selected object.
    - **Rotate**: Click the rotate option. A dialog box will appear where you can enter the degree of rotation.
    - **Resize**: Click the resize option. Enter the new length and width in the dialog box that appears.
    - **Change Outline Color**: Click the edit option under the edit menu. A dialog box will appear for you to choose a new color.

3. **Move**: Select the move option, then click and drag the object to the desired position. Click again to finalize the move.

#### Grouping and Ungrouping

1. **Select for Grouping**: Click on the group menu and select this option to start grouping.
2. **Group**: After selecting objects, click the group option to group them.
3. **Ungroup**: Select the group you want to ungroup, then click the ungroup option.
4. **Ungroup All**: Select the ungroup all option to ungroup all groups without selecting individual objects.

### Saving and Exporting

1. **Save as JPEG**: Select this option and enter the desired filename.
2. **Save as TXT**: Similar to saving as JPEG, but the file will be saved as a TXT.
3. **Export from JPEG**: Open any JPEG format file by entering the filename.
4. **Export as XML**: Export your file in XML format by entering the filename.

### Opening Files

- **Open**: Open files saved in TXT or XML format by entering the filename in the dialog box.

### Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes. Ensure to follow the existing coding style and include relevant tests.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
