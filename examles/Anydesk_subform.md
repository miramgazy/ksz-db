Option Compare Database

Private Sub anyId_DblClick(Cancel As Integer)
  Dim strText As String
    strText = Nz(Me.anyId.Value, "пусто")
    
    ' Копируем в буфер
    Call CopyTextToClipboard(strText)
    
    ' Обращаемся к родительской форме (Parent)
    With Me.Parent
        .lblNotification.Caption = "AnyDesk id: '" & strText & "' скопирован в буфер обмена!"
        .lblNotification.Visible = True
        
        ' Пауза перед очисткой
        Dim PauseTime As Single
        PauseTime = Timer + 0.7
        Do While Timer < PauseTime
            DoEvents
        Loop
        
        ' Очищаем сообщение на родительской форме
        .lblNotification.Caption = ""
        .lblNotification.Visible = False
    End With

End Sub

Private Sub anyPassword_DblClick(Cancel As Integer)
Dim strText As String
    strText = Nz(Me.anyPassword.Value, "пусто")
    
    ' Копируем в буфер
    Call CopyTextToClipboard(strText)
    
    ' Обращаемся к родительской форме (Parent)
    With Me.Parent
        .lblNotification.Caption = "Пароль от AnyDesk: '" & strText & "' скопирован в буфер обмена!"
        .lblNotification.Visible = True
        
        ' Пауза перед очисткой
        Dim PauseTime As Single
        PauseTime = Timer + 0.7
        Do While Timer < PauseTime
            DoEvents
        Loop
        
        ' Очищаем сообщение на родительской форме
        .lblNotification.Caption = ""
        .lblNotification.Visible = False
    End With
End Sub

Private Sub withPass_DblClick(Cancel As Integer)
    Dim anydeskID As String
    Dim anydeskPassword As String
    Dim shellCommand As String
    Dim anydeskPath As String
    Dim SandboxParams As String
    Dim IsSandbox As Boolean
    
    Dim sandmanPath As String
    sandmanPath = """C:\Program Files\Sandboxie-Plus\SandMan.exe""" ' Путь к загрузчику

    ' 1. Проверка ID
    If IsNull(Me!anyId) Or Trim(Me!anyId) = "" Then
        MsgBox "Поле anyId пустое.", vbExclamation
        Exit Sub
    End If
    anydeskID = Me!anyId.Value

    ' 2. Открытие формы выбора
    DoCmd.OpenForm "frmSelectVersion", , , , , acDialog
    
    ' 3. Считывание данных
    ' Проверяем, загружена ли форма (она будет загружена, если нажали кнопку и сработал Me.Visible = False)
    If CurrentProject.AllForms("frmSelectVersion").IsLoaded Then
        
        Dim selectedForm As Form
        Set selectedForm = Forms("frmSelectVersion")
        
        ' Используем проверку через переменную, которую мы объявили как Public
        If selectedForm.IsConfirmed = True Then
            
            ' ВАЖНО: Проверьте индексы!
            ' Column(0) - Название, Column(1) - Путь, Column(2) - Sandbox (Да/Нет)
            anydeskPath = """" & selectedForm!lstVersions.column(1) & """"
            IsSandbox = selectedForm!lstVersions.column(2)
            SandboxParams = Nz(selectedForm!lstVersions.column(3), "")
            
            DoCmd.Close acForm, "frmSelectVersion"
        Else
            ' Если нажали "Отмена" или закрыли крестиком внутри формы
            DoCmd.Close acForm, "frmSelectVersion"
            Exit Sub
        End If
    Else
        ' Если пользователь закрыл форму на системный крестик (X) в углу окна
        Exit Sub
    End If

    ' 4. Формирование базовой команды запуска
    If IsSandbox Then
        ' Для Sandboxie: "SandMan.exe" /box:Имя "Путь_к_AnyDesk" ID
        shellCommand = sandmanPath & " " & SandboxParams & " " & anydeskPath & " " & anydeskID
    Else
        ' Обычный запуск: "Путь_к_AnyDesk" ID
        shellCommand = anydeskPath & " " & anydeskID
    End If

    ' 5. Умная обработка пароля
    If Not IsNull(Me!anyPassword) And Trim(Me!anyPassword) <> "" Then
        anydeskPassword = Me!anyPassword.Value
        
        If IsSandbox Then
            ' ВАРИАНТ А: Для песочницы просто копируем в буфер
            Call CopyTextToClipboard(anydeskPassword)
            
            ' Выводим уведомление в основную форму (Parent)
            With Me.Parent
                .lblNotification.Caption = "Пароль скопирован! Вставьте его в AnyDesk вручную."
                .lblNotification.Visible = True
            End With
        Else
            ' ВАРИАНТ Б: Для стандарта оставляем ваш старый метод с авто-входом
            ' Этот метод полностью перезаписывает shellCommand для системного обработчика
            shellCommand = "rundll32.exe url.dll,FileProtocolHandler clearbat://anydesk@" & anydeskID & ":" & anydeskPassword
        End If
    End If

    ' 6. Финальный запуск
    ' Теперь shellCommand содержит либо путь к Sandbox, либо строку rundll32
    Shell shellCommand, vbNormalFocus

End Sub

Private Sub Поле196_DblClick(Cancel As Integer)
    Dim anydeskPath As String
    Dim anydeskID As String
    Dim anydeskPassword As String
    Dim shellCommand As String
    
    ' Путь к файлу AnyDesk
    anydeskPath = """C:\Program Files (x86)\AnyDesk\AnyDesk.exe"""
    
    ' Проверяем, существует ли поле anyId и содержит ли оно значение
    If IsNull(Me!anyId) Or Me!anyId = "" Then
        MsgBox "Поле anyId пустое. Пожалуйста, укажите ID AnyDesk.", vbExclamation
        Exit Sub
    End If
    
    ' Получаем значение поля anyId
    anydeskID = Me!anyId.Value
    
    ' Проверяем, существует ли поле anyPassword и содержит ли оно значение
    If Not IsNull(Me!anyPassword) Or Me!anyPassword <> "" Then
        ' Если пароль указан, добавляем его в команду
        anydeskPassword = Me!anyPassword.Value
        shellCommand = anydeskPath & " " & anydeskID & " --with-password " & anydeskPassword
    Else
        ' Если пароль не указан, запускаем только с ID
        shellCommand = anydeskPath & " " & anydeskID
    End If
    
    ' Запускаем AnyDesk
    Shell shellCommand, vbNormalFocus
End Sub


Private Sub Поле226_DblClick(Cancel As Integer)
    Dim anydeskPath As String
    Dim anydeskID As String
    Dim anydeskPassword As String
    Dim shellCommand As String
    
    ' Путь к файлу AnyDesk
    anydeskPath = """C:\Program Files (x86)\AnyDesk\AnyDesk.exe"""
    
    ' Проверяем, существует ли поле anyId и содержит ли оно значение
    If IsNull(Me!anyId) Or Me!anyId = "" Then
        MsgBox "Поле anyId пустое. Пожалуйста, укажите ID AnyDesk.", vbExclamation
        Exit Sub
    End If
    
    ' Получаем значение поля anyId
    anydeskID = Me!anyId.Value
    
    ' Проверяем, существует ли поле anyPassword и содержит ли оно значение
    If Not IsNull(Me!anyPassword) Or Me!anyPassword <> "" Then
        ' Если пароль указан, добавляем его в команду
        anydeskPassword = Me!anyPassword.Value
        shellCommand = anydeskPath & " " & anydeskID & " --with-password " & anydeskPassword
    Else
        ' Если пароль не указан, запускаем только с ID
        shellCommand = anydeskPath & " " & anydeskID
    End If
    
    ' Запускаем AnyDesk
    Shell shellCommand, vbNormalFocus
End Sub
