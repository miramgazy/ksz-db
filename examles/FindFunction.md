Attribute VB_Name = "FindFunction"
Option Compare Text ' Для нечувствительности к регистру при поиске

Public Sub HighlightFirstMatch(frm As Form, searchText As String)
    Dim rs As DAO.Recordset
    Dim column As DAO.Field
    Dim matchFound As Boolean

    ' Получаем Recordset текущей формы
    Set rs = frm.RecordsetClone
    rs.MoveFirst

    matchFound = False

    ' Перебираем записи
    Do Until rs.EOF
        ' Проверяем каждое поле записи
        For Each column In rs.Fields
            If Not IsNull(column.Value) And InStr(1, column.Value & "", searchText, vbTextCompare) > 0 Then
                ' Если нашли совпадение, перемещаемся на эту запись
                frm.Bookmark = rs.Bookmark
                matchFound = True
                Exit For
            End If
        Next column

        If matchFound Then Exit Do
        rs.MoveNext
    Loop

    ' Если совпадений нет
    If Not matchFound Then
        MsgBox "Совпадений не найдено.", vbInformation, "Поиск"
    End If

    ' Освобождаем ресурсы
    Set rs = Nothing
End Sub

Public Sub HighlightNextMatch(frm As Form, searchText As String)
    Dim rs As DAO.Recordset
    Dim column As DAO.Field
    Dim matchFound As Boolean

    ' Получаем Recordset текущей формы
    Set rs = frm.RecordsetClone
    rs.Bookmark = frm.Bookmark  ' Устанавливаем текущую позицию
    rs.MoveNext                ' Начинаем со следующей записи

    matchFound = False

    ' Перебираем записи
    Do Until rs.EOF
        For Each column In rs.Fields
            If Not IsNull(column.Value) And InStr(1, column.Value & "", searchText, vbTextCompare) > 0 Then
                ' Если нашли совпадение, перемещаемся на эту запись
                frm.Bookmark = rs.Bookmark
                matchFound = True
                Exit For
            End If
        Next column

        If matchFound Then Exit Do
        rs.MoveNext
    Loop

    ' Если совпадений больше нет
    If Not matchFound Then
        MsgBox "Совпадений больше нет.", vbInformation, "Поиск завершен"
    End If

    ' Освобождаем ресурсы
    Set rs = Nothing
End Sub

