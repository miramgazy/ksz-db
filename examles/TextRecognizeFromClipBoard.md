Attribute VB_Name = "TextRecognizeFromClipBoard"
Option Compare Database
Option Explicit

Private Const TESSERACT_PATH As String = "C:\Program Files\Tesseract-OCR\tesseract.exe"
Private Const NIRCMD_PATH As String = "C:\Program Files\Tesseract-OCR\Tools\nircmd.exe"

Private Function GetTmpPicturePath() As String
    GetTmpPicturePath = Environ("USERPROFILE") & "\Pictures\TmpPicture"
End Function
Private Sub EnsureTmpPictureFolderExists()
    Dim tmpPath As String
    tmpPath = GetTmpPicturePath()
    Dim fso As Object
    Set fso = CreateObject("Scripting.FileSystemObject")
    If Not fso.FolderExists(tmpPath) Then
        fso.CreateFolder tmpPath
    End If
End Sub

Private Sub Pause(seconds As Single)
    Dim endTime As Single
    endTime = Timer + seconds
    Do While Timer < endTime
        DoEvents
    Loop
End Sub

Private Function SaveClipboardImage(imagePath As String) As Boolean
    On Error GoTo ErrorHandler

    Pause 1 ' пауза 1 секунда

    Dim cmd As String
    cmd = """" & NIRCMD_PATH & """" & " clipboard saveimage " & """" & imagePath & """"

    Dim wsh As Object
    Set wsh = CreateObject("WScript.Shell")
    wsh.CurrentDirectory = GetTmpPicturePath()

    Dim exitCode As Integer
    exitCode = wsh.Run("cmd /c " & cmd, 0, True)

    SaveClipboardImage = (Dir(imagePath) <> "")
    Exit Function

ErrorHandler:
    SaveClipboardImage = False
End Function
Private Sub ShellExecuteCommand(cmd As String, wait As Boolean, Optional hideWindow As Boolean = False)
    Dim wsh As Object
    Set wsh = CreateObject("WScript.Shell")
    Dim windowStyle As Integer
    windowStyle = IIf(hideWindow, 0, 1)
    If wait Then
        wsh.Run "cmd /c " & cmd, windowStyle, True
    Else
        wsh.Run "cmd /c " & cmd, windowStyle, False
    End If
End Sub
Private Function RecognizeTextFromImage(imagePath As String) As String
    On Error GoTo ErrorHandler

    Dim outputFilePath As String
    outputFilePath = GetTmpPicturePath() & "\AnyDeskOCR_Result"

    ' Удаляем старый результат
    If Dir(outputFilePath & ".txt") <> "" Then Kill outputFilePath & ".txt"

    Dim command As String
    command = "cmd /c " & Chr(34) & Chr(34) & TESSERACT_PATH & Chr(34) & " " & Chr(34) & imagePath & Chr(34) & " " & Chr(34) & outputFilePath & Chr(34) & " --psm 6 -c tessedit_char_whitelist=0123456789" & Chr(34)
    
    'command = """" & TESSERACT_PATH & """ """ & imagePath & """ """ & outputFilePath & """ --psm 6"

    ' Запускаем команду
    ShellExecuteCommand command, True, True

    ' Проверяем, есть ли результат
    Dim resultFile As String
    resultFile = outputFilePath & ".txt"
    If Dir(resultFile) = "" Then
        MsgBox "Ошибка OCR: Tesseract не создал результат.", vbCritical
        RecognizeTextFromImage = ""
        Exit Function
    End If

    ' Читаем результат
    Dim result As String, fNum As Integer
    fNum = FreeFile
    Open resultFile For Input As #fNum
    result = Input$(LOF(fNum), fNum)
    Close #fNum

    Kill resultFile
    RecognizeTextFromImage = Trim(result)
    Exit Function

ErrorHandler:
    MsgBox "Ошибка при OCR: " & Err.description, vbCritical
    RecognizeTextFromImage = ""
End Function
Public Function RecognizeAnyDeskText() As String
    On Error GoTo ErrorHandler

    Dim imagePath As String
    imagePath = GetTmpPicturePath() & "\AnyDeskOCR.png"

    ' Создаем папку TmpPicture, если её нет
    EnsureTmpPictureFolderExists

    ' Удаляем старый файл, если он есть
    If Dir(imagePath) <> "" Then Kill imagePath

    ' Сохраняем изображение с проверкой
    If Not SaveClipboardImageViaBat(imagePath) Then
        MsgBox "Не удалось сохранить изображение из буфера обмена!" & vbCrLf & _
               "Убедитесь, что в буфере обмена есть изображение.", vbExclamation
        RecognizeAnyDeskText = ""
        Exit Function
    End If

    ' Распознаем текст через Tesseract
    Dim recognizedText As String
    recognizedText = RecognizeTextFromImage(imagePath)

    ' Очищаем результат: оставляем только цифры
    recognizedText = OnlyDigits(recognizedText)

    ' Очищаем временный файл
    If Dir(imagePath) <> "" Then Kill imagePath

    RecognizeAnyDeskText = recognizedText
    Exit Function

ErrorHandler:
    MsgBox "Ошибка: " & Err.description, vbCritical
    RecognizeAnyDeskText = ""
End Function
Private Function SaveClipboardImageViaBat(imagePath As String) As Boolean
    On Error GoTo ErrorHandler

    ' Формируем команду для nircmd
    Dim cmd As String
    cmd = """" & NIRCMD_PATH & """" & " clipboard saveimage " & """" & imagePath & """"

    ' Путь к BAT-файлу
    Dim batPath As String
    batPath = GetTmpPicturePath() & "\run_nircmd.bat"

    ' Создаём BAT-файл и записываем команду
    Dim f As Integer
    f = FreeFile
    Open batPath For Output As #f
    Print #f, cmd
    Close #f

    ' Запускаем BAT-файл
    Shell "cmd /c """ & batPath & """", vbHide

    ' Даем время на выполнение команды
    Pause 1

    ' Проверяем, появился ли файл
    SaveClipboardImageViaBat = (Dir(imagePath) <> "")

    ' Удаляем BAT-файл
    If Dir(batPath) <> "" Then Kill batPath

    Exit Function

ErrorHandler:
    SaveClipboardImageViaBat = False
End Function
Private Function OnlyDigits(inputStr As String) As String
    Dim i As Integer, ch As String, result As String
    result = ""
    For i = 1 To Len(inputStr)
        ch = Mid(inputStr, i, 1)
        If ch >= "0" And ch <= "9" Then
            result = result & ch
        End If
    Next i
    OnlyDigits = result
End Function
