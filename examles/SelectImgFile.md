Attribute VB_Name = "SelectImgFile"
Option Compare Database

Public Function SelectImageFile() As String
    Dim fd As FileDialog
    Set fd = Application.FileDialog(msoFileDialogFilePicker)

    With fd
        .Title = "Выберите изображение с AnyDesk ID"
        .Filters.Clear
        .Filters.Add "Изображения", "*.png; *.jpg; *.jpeg; *.bmp"
        .AllowMultiSelect = False

        If .Show = -1 Then
            SelectImageFile = .SelectedItems(1)
        Else
            SelectImageFile = ""
        End If
    End With
End Function
