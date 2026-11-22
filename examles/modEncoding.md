Attribute VB_Name = "modEncoding"
Option Compare Database
Option Explicit

' Кодирование в Base64
Public Function EncodeBase64(ByVal plainText As String) As String
    If Len(plainText) = 0 Then
        EncodeBase64 = ""
        Exit Function
    End If

    Dim arr() As Byte
    arr = StrConv(plainText, vbFromUnicode)
    EncodeBase64 = EncodeBase64Binary(arr)
End Function

' Декодирование из Base64
Public Function DecodeBase64(ByVal encodedText As String) As String
    If Len(encodedText) = 0 Then
        DecodeBase64 = ""
        Exit Function
    End If

    Dim xml As Object
    Set xml = CreateObject("MSXML2.DOMDocument")
    Dim node As Object
    Set node = xml.createElement("b64")

    node.DataType = "bin.base64"
    node.Text = encodedText

    DecodeBase64 = StrConv(node.nodeTypedValue, vbUnicode)
End Function

' Вспомогательная функция для кодирования массива байтов
Private Function EncodeBase64Binary(ByRef arr() As Byte) As String
    Dim xml As Object
    Set xml = CreateObject("MSXML2.DOMDocument")
    Dim node As Object
    Set node = xml.createElement("b64")

    node.DataType = "bin.base64"
    node.nodeTypedValue = arr

    EncodeBase64Binary = Replace(node.Text, vbLf, "")
End Function

' === Массовое кодирование паролей в таблице main ===
Public Sub EncodeExistingPasswords()
    On Error GoTo ErrHandler

    Dim db As DAO.Database
    Dim rs As DAO.Recordset
    Dim originalPassword As String
    Dim encodedPassword As String
    Dim countUpdated As Long

    Set db = CurrentDb
    Set rs = db.OpenRecordset("SELECT id, system_admin_password FROM main", dbOpenDynaset)

    Do While Not rs.EOF
        originalPassword = Nz(rs!system_admin_password, "")

        ' Проверяем, что пароль не пустой и, вероятно, ещё не закодирован (нет символа "=")
        If Len(originalPassword) > 0 And InStr(originalPassword, "=") = 0 Then
            encodedPassword = EncodeBase64(originalPassword)

            rs.Edit
            rs!system_admin_password = encodedPassword
            rs.Update

            countUpdated = countUpdated + 1
        End If

        rs.MoveNext
    Loop

    MsgBox "? Кодирование завершено!" & vbCrLf & _
           "Обновлено записей: " & countUpdated, vbInformation

Cleanup:
    If Not rs Is Nothing Then rs.Close
    Set rs = Nothing
    Set db = Nothing
    Exit Sub

ErrHandler:
    MsgBox "Ошибка при кодировании: " & Err.description, vbCritical
    Resume Cleanup
End Sub


