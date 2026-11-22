Attribute VB_Name = "findPathToDB"
Option Compare Database
Option Explicit

' Функция проверки пути и принятия решения о запуске формы
Public Function CheckBackendPath() As Boolean
    Dim db As DAO.Database
    Dim rs As DAO.Recordset
    Dim backendPath As String
    
    Set db = CurrentDb
    
    ' Проверяем, есть ли сохранённый путь
    On Error Resume Next
    Set rs = db.OpenRecordset("SELECT BackendPath FROM Settings WHERE ID = 1")
    If rs.EOF Then
        CheckBackendPath = False ' Нет пути, открываем frmStartup
    Else
        backendPath = rs("BackendPath")
        ' Проверяем, существует ли файл
        If Dir(backendPath) = "" Then
            CheckBackendPath = False ' Файл не найден, открываем frmStartup
        Else
            CheckBackendPath = True ' Файл найден, открываем Company List
        End If
    End If
    rs.Close
    Set rs = Nothing
End Function
