Attribute VB_Name = "TextRecognizeModule"
Option Compare Database
Option Explicit

Private Const TESSERACT_PATH As String = "C:\Program Files\Tesseract-OCR\tesseract.exe"

Public Function RecognizeAnyDeskIDFromFile(imagePath As String) As String
    On Error GoTo ErrorHandler

    If Dir(imagePath) = "" Then
        MsgBox "Файл изображения не найден!", vbExclamation
        Exit Function
    End If

    Dim rawText As String
    rawText = RecognizeTextFromImage(imagePath)

    Dim cleanID As String
    cleanID = ExtractAnyDeskID(rawText)

    RecognizeAnyDeskIDFromFile = cleanID
    Exit Function

ErrorHandler:
    MsgBox "Ошибка: " & Err.description, vbCritical
    RecognizeAnyDeskIDFromFile = ""
End Function

Private Function RecognizeTextFromImage(imagePath As String) As String
    On Error GoTo ErrorHandler

    Dim TEMP_RESULT As String
    TEMP_RESULT = Environ("TEMP") & "\AnyDeskOCR_Result"

    If Dir(TEMP_RESULT & ".txt") <> "" Then Kill TEMP_RESULT & ".txt"

    Dim command As String
    command = "cmd /c " & Chr(34) & Chr(34) & TESSERACT_PATH & Chr(34) & " " & Chr(34) & imagePath & Chr(34) & " " & Chr(34) & TEMP_RESULT & Chr(34) & " --psm 6 -c tessedit_char_whitelist=0123456789" & Chr(34)
    
    Dim oShell As Object
    Set oShell = CreateObject("WScript.Shell")
    Dim exec As Object
    Set exec = oShell.exec(command)

    Dim stdErr As String
    stdErr = exec.stdErr.ReadAll

    Dim txtFile As String
    txtFile = TEMP_RESULT & ".txt"

    If Dir(txtFile) = "" Then
        MsgBox "Ошибка OCR, результат не получен." & vbCrLf & "STDERR: " & stdErr, vbCritical
        Exit Function
    End If

    Dim result As String
    Dim fileNum As Integer
    fileNum = FreeFile
    Open txtFile For Input As #fileNum
    result = Input$(LOF(fileNum), fileNum)
    Close #fileNum

    Kill txtFile

    RecognizeTextFromImage = Trim(result)
    Exit Function

ErrorHandler:
    MsgBox "Ошибка при OCR: " & Err.description, vbCritical
    RecognizeTextFromImage = ""
End Function

Private Function ExtractAnyDeskID(rawText As String) As String
    Dim i As Integer, cleanText As String, ch As String

    For i = 1 To Len(rawText)
        ch = Mid(rawText, i, 1)
        If ch Like "#" Then cleanText = cleanText & ch
    Next i

    If cleanText = "" Then
        MsgBox "Не удалось найти цифры. Распознанный текст: " & rawText, vbExclamation
    End If

    ExtractAnyDeskID = cleanText
End Function
