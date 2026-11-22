Option Compare Database
Option Explicit
' Îáúÿâëåíèÿ Windows API
Private Declare PtrSafe Function ShowWindow Lib "user32" (ByVal hWnd As Long, ByVal nCmdShow As Long) As Long
Private Declare PtrSafe Function FindWindow Lib "user32" Alias "FindWindowA" (ByVal lpClassName As String, ByVal lpWindowName As String) As Long
Private Const SW_MINIMIZE As Long = 6 ' Ñâîðà÷èâàåì îêíî
Private Const SW_RESTORE As Long = 9  ' Âîññòàíàâëèâàåì îêíî

Private Function OpenFilterFavorites()

    On Error GoTo ErrorHandler
        
    ' show the control and drop down the combo box
    'Me.cboFilterFavorites.Visible = True
    'Me.cboFilterFavorites.SetFocus
    'Me.cboFilterFavorites.Dropdown
            
ExitProcedure:
    Exit Function
    
ErrorHandler:
    Resume ExitProcedure

End Function

Private Sub Ïîëå363_Click()
End Sub

Private Sub anyDesk_Click()
    Dim filePath As String
    Dim anydeskID As String

    ' Îòêðûâàåì äèàëîã âûáîðà èçîáðàæåíèÿ
    filePath = SelectImageFile()
    
    If filePath = "" Then Exit Sub ' Ïîëüçîâàòåëü îòìåíèë âûáîð

    ' Ðàñïîçíàåì AnyDesk ID
    anydeskID = RecognizeAnyDeskIDFromFile(filePath)
    
    If anydeskID <> "" Then
        Me.cboAnyDeskId = anydeskID  ' Âàøå ïîëå äëÿ âûâîäà ID
        Me.cboAnyDeskId.SetFocus     ' Ñòàâèì ôîêóñ íà ïîëå
        'MsgBox "AnyDesk ID ðàñïîçíàí: " & anydeskID, vbInformation
    End If
End Sub

Private Sub LaunchAnyDesk(anydeskID As String)
    On Error GoTo ErrorHandler
    
    Dim anydeskPath As String
    Dim shellCommand As String
    Dim rs As DAO.Recordset
    
    If anydeskID = "" Then Exit Sub
    
    ' Ïðîâåðêà ïóòè ê AnyDesk
    anydeskPath = "C:\Program Files (x86)\AnyDesk\AnyDesk.exe"
    If Dir(anydeskPath) = "" Then
        MsgBox "Ôàéë AnyDesk.exe íå íàéäåí. Ïðîâåðüòå ïóòü.", vbCritical
        Exit Sub
    End If
    
    ' Ïðîâåðêà ñóùåñòâîâàíèÿ ID â áàçå (áåç ïàðàìåòðèçîâàííîãî çàïðîñà äëÿ ïðîñòîòû)
    Set rs = CurrentDb.OpenRecordset("SELECT * FROM anydesk_cash WHERE anydeskId = '" & Replace(anydeskID, "'", "''") & "'")
    
    If rs.EOF Then
        ' Äîáàâëåíèå íîâîãî ID
        CurrentDb.Execute "INSERT INTO anydesk_cash (anydeskId, usageCount) VALUES ('" & Replace(anydeskID, "'", "''") & "', 1)"
    Else
        ' Óâåëè÷åíèå ñ÷¸ò÷èêà
        rs.Edit
        rs!usageCount = rs!usageCount + 1
        rs.Update
    End If
    rs.Close
    
    ' Îáíîâëåíèå ComboBox
    Me.cboAnyDeskId.Requery
    
    ' Çàïóñê AnyDesk
    shellCommand = Chr(34) & anydeskPath & Chr(34) & " --destination " & anydeskID
    Shell shellCommand, vbNormalFocus
    
    Exit Sub
    
ErrorHandler:
    MsgBox "Îøèáêà: " & Err.description, vbCritical
End Sub

Private Sub btm_encoder_Click()
 Dim inputPassword As String

    ' Ïðèíóäèòåëüíî îáíîâëÿåì äàííûå âñåõ ïîëåé ôîðìû
    Me.txtGeneratedPassword.SetFocus
    Me.txtGeneratedPassword = Me.txtGeneratedPassword.Text
    Me.Refresh

    ' Òåïåðü ÷èòàåì çíà÷åíèå
    inputPassword = Trim(Me.txtGeneratedPassword.Value)

    If inputPassword = "" Then
        MsgBox "Ââåäèòå ïàðîëü äëÿ êîäèðîâàíèÿ.", vbExclamation, "Îøèáêà"
        Exit Sub
    End If

    ' Êîäèðóåì è âûâîäèì ðåçóëüòàò
    Me.encPass = EncodeBase64(inputPassword)

End Sub

Private Sub cboAnyDeskId_KeyDown(KeyCode As Integer, Shift As Integer)
 If KeyCode = vbKeyReturn Then
        Dim enteredId As String
        
        ' 1. Áåðåì òåêñò ïðÿìî èç ïîëÿ ââîäà (ñâîéñòâî .Text)
        ' Èñïîëüçóåì Nz, ÷òîáû íå áûëî îøèáêè, åñëè ïîëå ñîâñåì ïóñòîå
        enteredId = Replace(Nz(Me.cboAnyDeskId.Text, ""), " ", "")
        enteredId = Trim(enteredId)
        
        ' 2. Ïðîâåðÿåì ID
        If enteredId = "" Then
            MsgBox "Ââåäèòå ID AnyDesk!", vbExclamation
            Exit Sub
        End If
        
        ' 3. Òåïåðü ïðèíóäèòåëüíî ñîõðàíÿåì çíà÷åíèå â ïîëå,
        ' ÷òîáû îíî íå ñòåðëîñü ïðè îòêðûòèè äðóãîé ôîðìû
        Me.cboAnyDeskId = enteredId

        ' 4. Îòêðûâàåì óïðîùåííóþ ôîðìó âûáîðà
        DoCmd.OpenForm "frmSelectVersion_simply", , , , , acDialog
        
        ' 5. Îáðàáîòêà âûáîðà (êîä îñòàåòñÿ ïðåæíèì)
        If CurrentProject.AllForms("frmSelectVersion_simply").IsLoaded Then
            If Forms("frmSelectVersion_simply").IsConfirmed = True Then
                
                Dim anyPath As String, sandParams As String, isSand As Boolean
                With Forms("frmSelectVersion_simply")!lstVersions
                    anyPath = """" & .column(1) & """"
                    isSand = .column(2)
                    sandParams = Nz(.column(3), "")
                End With
                
                DoCmd.Close acForm, "frmSelectVersion_simply"
                
                ' Çàïóñê
                LaunchAnyDeskNow enteredId, anyPath, isSand, sandParams
                
            Else
                DoCmd.Close acForm, "frmSelectVersion_simply"
            End If
        End If
        
        KeyCode = 0 ' Óáèðàåì ñèñòåìíûé çâóê
    End If
End Sub

' Óïðîùåííàÿ ïðîöåäóðà çàïóñêà (âñòàâüòå íèæå â òîì æå ìîäóëå)
Private Sub LaunchAnyDeskNow(anyID As String, anyPath As String, isSand As Boolean, sandParams As String)
    Dim shellCommand As String
    Dim sandmanPath As String
    sandmanPath = """C:\Program Files\Sandboxie-Plus\SandMan.exe"""

    If isSand Then
        shellCommand = sandmanPath & " " & sandParams & " " & anyPath & " " & anyID
    Else
        shellCommand = anyPath & " " & anyID
    End If

    Shell shellCommand, vbNormalFocus
End Sub


Private Sub Auto_Title0_Click()
If IsNull(Me.select_iikoRosta) Then
Me.FilterOn = False

Else
Me.Filter = "iiko_rosta=" & Me.select_iikoRosta
Me.FilterOn = True
End If

Me.OrderBy = "sort_number DESC, id ASC"
    Me.OrderByOn = True
Me.Refresh
End Sub

Private Sub backOffice_DblClick(Cancel As Integer)
    Dim serverAddress As String
    Dim portN As String
    Dim sysAdminName As String
    Dim sysadminPassFromDB As String
    Dim plainPass As String
    Dim rawParams As String
    Dim finalBase64 As String
    Dim fullURL As String
    Dim shellCmd As String

    ' 1. Ïðîâåðêà çàïîëíåíèÿ ïîëåé
    If Nz(Me!server_name, "") = "" Or Nz(Me!portN, "") = "" Or _
       Nz(Me!sysadminlogin, "") = "" Or Nz(Me!sysadminPass, "") = "" Then
        MsgBox "Çàïîëíèòå âñå äàííûå!", vbExclamation
        Exit Sub
    End If

    ' 2. Ïîëó÷àåì çíà÷åíèÿ èç ôîðìû
    serverAddress = Trim(Me!server_name)
    portN = Trim(Me!portN)
    sysAdminName = Trim(Me!sysadminlogin)
    sysadminPassFromDB = Trim(Me!sysadminPass) ' Ïàðîëü â Base64 èç áàçû

    ' 3. ÐÀÑØÈÔÐÎÂÊÀ: Ïîëó÷àåì ÷èñòûé òåêñòîâûé ïàðîëü
    ' Èñïîëüçóåì âàøó ôóíêöèþ Base64Decode
    plainPass = Base64Decode(sysadminPassFromDB)
    If plainPass = "" Then plainPass = sysadminPassFromDB

    ' 4. ÔÎÐÌÈÐÎÂÀÍÈÅ ÏÀÐÀÌÅÒÐÎÂ (V2)
    ' Ñîáèðàåì ñòðîêó â ôîðìàòå: ?type=iiko?url=host:port?login=user?password=pass
    rawParams = "?type=iiko?url=" & serverAddress & ":" & portN & _
                "?login=" & sysAdminName & "?password=" & plainPass

    ' 5. ÏÎËÍÎÅ ÊÎÄÈÐÎÂÀÍÈÅ ÑÒÐÎÊÈ
    ' Èñïîëüçóåì âàøó ôóíêöèþ Base64Encode äëÿ âñåé ñòðîêè ïàðàìåòðîâ
    finalBase64 = Base64Encode(rawParams)

    ' 6. ÈÒÎÃÎÂÛÉ URL
    ' Ïî íîâîé èíñòðóêöèè: îäèí ñëåø è ôëàã â êîíöå
    fullURL = "clearbat:/" & finalBase64 & "?encode=full"

    ' 7. ÇÀÏÓÑÊ ÏÐÎÃÐÀÌÌÛ
    On Error Resume Next
    shellCmd = "rundll32.exe url.dll,FileProtocolHandler """ & fullURL & """"
    Shell shellCmd, vbNormalFocus
    
    If Err.Number <> 0 Then
        MsgBox "Îøèáêà ïðè çàïóñêå. Ïðîâåðüòå óñòàíîâêó ClearBat.", vbCritical
    End If
    On Error GoTo 0

    ' 8. Ðàáîòà ñ áóôåðîì è óâåäîìëåíèåì
    ' Êîïèðóåì â áóôåð ÷èñòûé ðàñøèôðîâàííûé ïàðîëü
    Call CopyTextToClipboard(plainPass)
    
    Me.lblNotification.Caption = "Çàïóñê (V2 Full Encode)... Ïàðîëü â áóôåðå."
    Me.lblNotification.Visible = True

    Dim endTime As Double
    endTime = Timer + 1#
    Do While Timer < endTime: DoEvents: Loop

    Me.lblNotification.Visible = False
End Sub


Private Sub bottonPgUp_Click()
 On Error Resume Next
    ' Ïåðåìåùàåìñÿ íà ïîñëåäíèé çàïèñü òàáëèöû
    DoCmd.GoToRecord , , acFirst
End Sub

Private Sub btnClearSearch_Click()
    Me.txtSearch.Value = ""  ' Î÷èùàåì ïîëå ïîèñêà
    Me.Tag = ""  ' Ñáðàñûâàåì ñîñòîÿíèå ïîèñêà
    Me.txtSearch.SetFocus  ' Óñòàíàâëèâàåì ôîêóñ îáðàòíî â ïîëå ââîäà
End Sub

Private Sub btnNextSearch_Click()
Dim searchText As String
    searchText = Nz(Me.txtSearch.Value, "") ' Ïîëó÷àåì òåêñò èç ïîëÿ

    If searchText = "" Then
        MsgBox "Ââåäèòå òåêñò äëÿ ïîèñêà.", vbExclamation, "Ïîèñê"
        Exit Sub
    End If

    ' Âûçûâàåì ôóíêöèþ äëÿ ïîäñâåòêè ñëåäóþùåãî ñîâïàäåíèÿ
    Call HighlightNextMatch(Me, searchText)
End Sub

Private Sub btnScrollToBottom_Click()
 On Error Resume Next
    ' Ïåðåìåùàåìñÿ íà ïîñëåäíèé çàïèñü òàáëèöû
    DoCmd.GoToRecord , , acLast
End Sub


Private Sub chkEditMode_AfterUpdate()
Dim state As Boolean
    state = Me.chkEditMode.Value
    
    ' Ðàçðåøàåì ðåäàêòèðîâàíèå ïîëåé
    Me.facilityName.Locked = Not state
    Me.crmid.Locked = Not state
    Me.uid.Locked = Not state
    Me.server_name.Locked = Not state
    Me.portN.Locked = Not state
    Me.sysadminlogin.Locked = Not state
    Me.sysadminPass.Locked = Not state

End Sub

Private Sub chkStatus_AfterUpdate()
If Me.chkStatus = True Then
        Me.Filter = "iiko_rosta = " & Me.select_iikoRosta & " AND status = True"
    Else
        Me.Filter = "status = False"
    End If
    Me.FilterOn = True
End Sub

Private Sub cmdClose_Click()
DoCmd.Quit
End Sub

Private Sub cmdRecognizeAnyDeskID_Click()
    Dim anydeskID As String

   ' Ðàñïîçíàåì AnyDesk ID
    anydeskID = RecognizeAnyDeskText()
    
    If anydeskID <> "" Then
        Me.cboAnyDeskId = anydeskID  ' Âàøå ïîëå äëÿ âûâîäà ID
        Me.cboAnyDeskId.SetFocus     ' Ñòàâèì ôîêóñ íà ïîëå
        'MsgBox "AnyDesk ID ðàñïîçíàí: " & anydeskID, vbInformation
    End If
End Sub

Private Sub co_list_Click()
If IsNull(Me.co_list) Then
Me.FilterOn = False

Else
Me.Filter = "sort_number=" & Me.co_list
Me.FilterOn = True
End If
End Sub

Private Sub crmId_DblClick(Cancel As Integer)
On Error Resume Next
Dim strText As String
    strText = Nz(Me.crmid.Value, "ïóñòî")
    Call CopyTextToClipboard(strText)
    
    ' Ïîêàçûâàåì ñîîáùåíèå
    Me.lblNotification.Caption = "CRMID: '" & strText & "' ñêîïèðîâàí â áóôåð îáìåíó!"
    Me.lblNotification.Visible = True

    ' Ïàóçà ïåðåä î÷èñòêîé
    Dim PauseTime As Single
    PauseTime = Timer + 0.5 ' 1 ñåêóíäà
    Do While Timer < PauseTime
        DoEvents
    Loop

    ' Î÷èùàåì ñîîáùåíèå
    Me.lblNotification.Caption = ""
    Me.lblNotification.Visible = False
    
End Sub

Private Sub encPass_AfterUpdate()

End Sub

Private Sub encPass_DblClick(Cancel As Integer)
Dim strText As String
    strText = Nz(Me.encPass.Value, "ïóñòî")
    Call CopyTextToClipboard(strText)
    
    ' Ïîêàçûâàåì ñîîáùåíèå
    Me.lblNotification.Caption = "Ñãåíåðèðîâàííûé è çàêîäèðîâàííûé ïàðîëü: '" & strText & "' ñêîïèðîâàí â áóôåð îáìåíó!"
    Me.lblNotification.Visible = True

    ' Ïàóçà ïåðåä î÷èñòêîé
    Dim PauseTime As Single
    PauseTime = Timer + 0.5 ' 1 ñåêóíäà
    Do While Timer < PauseTime
        DoEvents
    Loop

    ' Î÷èùàåì ñîîáùåíèå
    Me.lblNotification.Caption = ""
    Me.lblNotification.Visible = False
End Sub

Private Sub Form_BeforeInsert(Cancel As Integer)
On Error Resume Next
' Óñòàíàâëèâàåì òåêóùóþ äàòó è âðåìÿ òîëüêî ïðè äîáàâëåíèè íîâîé çàïèñè
    Me.CreationDate = Now
End Sub
Private Sub Form_Load()
    On Error Resume Next
    ' Íàõîäèì îêíî Access
    Dim hWnd As Long
    hWnd = FindWindow("OMain", vbNullString) ' "OMain" - êëàññ îêíà Access
    ' Ñâîðà÷èâàåì îêíî Access, îñòàâëÿÿ çíà÷îê íà ïàíåëè çàäà÷
    ShowWindow hWnd, SW_MINIMIZE
    ' Óñòàíàâëèâàåì øèðèíó ôîðìû
    Me.Width = 19190 ' 33,862 ñì
    Me.Visible = True
    
    If Me.chkStatus = True Then
        Me.Filter = "status = True"
        Me.Filter = "iiko_rosta=" & Me.select_iikoRosta
    Else
        Me.Filter = "status = False"
    End If
    Me.FilterOn = True
    On Error GoTo 0
End Sub

Private Sub Form_Resize()
    On Error Resume Next
    Me.Width = 19190 ' Ôèêñèðóåì øèðèíó
    On Error GoTo 0
End Sub
Private Sub Form_Unload(Cancel As Integer)
    'Âîññòàíàâëèâàåì îêíî Access ïðè çàêðûòèè ôîðìû (îïöèîíàëüíî)
    Dim hWnd As Long
    hWnd = FindWindow("OMain", vbNullString)
    ShowWindow hWnd, SW_RESTORE
End Sub

Private Sub Form_Open(Cancel As Integer)
' Ñâîðà÷èâàåì ãëàâíîå îêíî Access
    DoCmd.RunCommand acCmdAppMinimize
    DoCmd.Maximize
    'Me.select_iikoRosta.Value = "1" ' Óñòàíîâèòü çíà÷åíèå ïî óìîë÷àíèþ
    Me.chkEditMode.Value = False
    
    Dim state As Boolean
    state = Me.chkEditMode.Value
    
    ' Ðàçðåøàåì ðåäàêòèðîâàíèå ïîëåé
    Me.facilityName.Locked = Not state
    Me.crmid.Locked = Not state
    Me.uid.Locked = Not state
    Me.server_name.Locked = Not state
    Me.portN.Locked = Not state
    Me.sysadminlogin.Locked = Not state
    Me.sysadminPass.Locked = Not state

    
End Sub


Private Sub select_iikoRosta_AfterUpdate()
Me.Refresh
End Sub
Private Sub iikoVersion_DblClick(Cancel As Integer)
Dim strText As String
    strText = Nz(Me.linkYa.Value, "ïóñòî") & "?=" & Nz(Me.server_name.Value, "ïóñòî")
    Call CopyTextToClipboard(strText)
    
    ' Ïîêàçûâàåì ñîîáùåíèå
    Me.lblNotification.Caption = "Àäðåñ ññûëêè: '" & strText & "' íà ñêà÷èâàíèÿ iiko Office èç ßíäåêñ äèñêà ñêîïèðîâàí â áóôåð îáìåíó!"
    Me.lblNotification.Visible = True

    ' Ïàóçà ïåðåä î÷èñòêîé
    Dim PauseTime As Single
    PauseTime = Timer + 0.7 ' 1 ñåêóíäà
    Do While Timer < PauseTime
        DoEvents
    Loop

    ' Î÷èùàåì ñîîáùåíèå
    Me.lblNotification.Caption = ""
    Me.lblNotification.Visible = False
End Sub

Private Sub pictureLink_DblClick(Cancel As Integer)
Dim link As String
    link = "https://bg.mevent.kz?text=" & Me.crmid
    Application.FollowHyperlink link
End Sub

Private Sub select_iikoRosta_Click()
If IsNull(Me.select_iikoRosta) Then
Me.FilterOn = False

Else
Me.Filter = "iiko_rosta=" & Me.select_iikoRosta
Me.FilterOn = True
End If

Me.OrderBy = "sort_number DESC, id ASC"
    Me.OrderByOn = True

End Sub

Private Sub serchBtn_Click()
Dim searchText As String
    searchText = Nz(Me.txtSearch.Value, "") ' Ïîëó÷àåì òåêñò èç ïîëÿ

    If searchText = "" Then
        MsgBox "Ââåäèòå òåêñò äëÿ ïîèñêà.", vbExclamation, "Ïîèñê"
        Exit Sub
    End If

    ' Âûçûâàåì ôóíêöèþ äëÿ ïîäñâåòêè ïåðâîãî ñîâïàäåíèÿ
    Call HighlightFirstMatch(Me, searchText)
End Sub

Private Sub server_name_DblClick(Cancel As Integer)
    Dim strText As String
    strText = Nz(Me.server_name.Value, "ïóñòî")
    Call CopyTextToClipboard(strText)
    
    ' Ïîêàçûâàåì ñîîáùåíèå
    Me.lblNotification.Caption = "Àäðåñ ñåðâåðà: '" & strText & "' ñêîïèðîâàí â áóôåð îáìåíó!"
    Me.lblNotification.Visible = True

    ' Ïàóçà ïåðåä î÷èñòêîé
    Dim PauseTime As Single
    PauseTime = Timer + 0.7 ' 1 ñåêóíäà
    Do While Timer < PauseTime
        DoEvents
    Loop

    ' Î÷èùàåì ñîîáùåíèå
    Me.lblNotification.Caption = ""
    Me.lblNotification.Visible = False
        
End Sub


Private Sub sysadminlogin_DblClick(Cancel As Integer)
Dim strText As String
    strText = Nz(Me.sysadminlogin.Value, "ïóñòî")
    Call CopyTextToClipboard(strText)
    
    ' Ïîêàçûâàåì ñîîáùåíèå
    Me.lblNotification.Caption = "Login ñèñÀäìèíà: '" & strText & "' ñêîïèðîâàí â áóôåð îáìåíó!"
    Me.lblNotification.Visible = True

    ' Ïàóçà ïåðåä î÷èñòêîé
    Dim PauseTime As Single
    PauseTime = Timer + 0.7 ' 1 ñåêóíäà
    Do While Timer < PauseTime
        DoEvents
    Loop

    ' Î÷èùàåì ñîîáùåíèå
    Me.lblNotification.Caption = ""
    Me.lblNotification.Visible = False
    
End Sub

Private Sub sysadminPass_DblClick(Cancel As Integer)
    Dim strText As String
    Dim decodedText As String
    Dim re As Object
    Dim isBase64 As Boolean

    ' Áåð¸ì çíà÷åíèå èç ïîëÿ
    strText = Nz(Me.sysadminPass.Value, "")

    ' Ïðîâåðÿåì, âûãëÿäèò ëè ýòî êàê Base64 (òîëüêî áóêâû, öèôðû, +, /, =)
    Set re = CreateObject("VBScript.RegExp")
    re.Pattern = "^[A-Za-z0-9+/=]+$"
    re.IgnoreCase = True
    re.Global = False
    isBase64 = re.Test(strText)

    ' Åñëè ýòî Base64, ïðîáóåì äåêîäèðîâàòü
    If isBase64 Then
        On Error Resume Next
        decodedText = DecodeBase64(strText)
        If Err.Number <> 0 Or decodedText = "" Then
            decodedText = strText ' åñëè íå óäàëîñü äåêîäèðîâàòü — îñòàâëÿåì îðèãèíàë
        End If
        On Error GoTo 0
    Else
        decodedText = strText
    End If

    ' Êîïèðóåì ðàñøèôðîâàííûé ïàðîëü â áóôåð îáìåíà
    Call CopyTextToClipboard(decodedText)
    
    ' Ïîêàçûâàåì ñîîáùåíèå ïîëüçîâàòåëþ
    Me.lblNotification.Caption = "Ïàðîëü ñèñòåìíîãî àäìèíèñòðàòîðà: '" & decodedText & "' ñêîïèðîâàí â áóôåð îáìåíà!"
    Me.lblNotification.Visible = True

    ' Ïàóçà 0.7 ñåêóíäû
    Dim PauseTime As Single
    PauseTime = Timer + 0.7
    Do While Timer < PauseTime
        DoEvents
    Loop

    ' Î÷èùàåì óâåäîìëåíèå
    Me.lblNotification.Caption = ""
    Me.lblNotification.Visible = False
End Sub

Private Sub btnGeneratePassword_Click()
    ' Ãåíåðàöèÿ ïàðîëÿ ñ çàäàííîé äëèíîé
    Dim PasswordLength As Integer
    Dim generatedPassword As String

    ' Ïðîâåðêà äëèíû ïàðîëÿ èç òåêñòîâîãî ïîëÿ
    If IsNumeric(Me.txtPasswordLength.Value) And Me.txtPasswordLength.Value > 0 Then
        PasswordLength = Me.txtPasswordLength.Value
    Else
        MsgBox "Ââåäèòå êîððåêòíîå ÷èñëî äëÿ äëèíû ïàðîëÿ.", vbExclamation, "Îøèáêà"
        Exit Sub
    End If

     ' Ãåíåðèðóåì ïàðîëü
    generatedPassword = GenerateRandomPassword(PasswordLength)

    ' Âûâîäèì ïàðîëü â ïîëå
    Me.txtGeneratedPassword = generatedPassword
    
    ' Êîäèðóåì è âûâîäèì â ïîëå encPass
    Me.encPass = EncodeBase64(generatedPassword)
End Sub

Public Function GenerateRandomPassword(PasswordLength As Integer) As String
    Dim Characters As String
    Dim Password As String
    Dim i As Integer
    Dim RandomIndex As Integer

    ' Ñòðîêà ñèìâîëîâ, èç êîòîðûõ áóäåò ôîðìèðîâàòüñÿ ïàðîëü
    Characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()"

    ' Èíèöèàëèçàöèÿ ãåíåðàòîðà ñëó÷àéíûõ ÷èñåë
    Randomize Timer

    ' Ãåíåðàöèÿ ïàðîëÿ
    Password = ""
    For i = 1 To PasswordLength
        RandomIndex = Int((Len(Characters) * Rnd) + 1)
        Password = Password & Mid(Characters, RandomIndex, 1)
    Next i

    ' Âîçâðàùàåì ðåçóëüòàò
    GenerateRandomPassword = Password
End Function

Private Sub txtGeneratedPassword_DblClick(Cancel As Integer)
 Dim strText As String
    strText = Nz(Me.txtGeneratedPassword.Value, "ïóñòî")
    Call CopyTextToClipboard(strText)
    
    ' Ïîêàçûâàåì ñîîáùåíèå
    Me.lblNotification.Caption = "Ñãåíåðèðîâàííûé ïàðîëü: '" & strText & "' ñêîïèðîâàí â áóôåð îáìåíó!"
    Me.lblNotification.Visible = True

    ' Ïàóçà ïåðåä î÷èñòêîé
    Dim PauseTime As Single
    PauseTime = Timer + 0.5 ' 1 ñåêóíäà
    Do While Timer < PauseTime
        DoEvents
    Loop

    ' Î÷èùàåì ñîîáùåíèå
    Me.lblNotification.Caption = ""
    Me.lblNotification.Visible = False
    
End Sub

Private Sub txtSearch_KeyDown(KeyCode As Integer, Shift As Integer)

If KeyCode = vbKeyReturn Then
Me.Refresh
        If Not IsNull(Me.txtSearch.Value) And Me.txtSearch.Value <> "" Then
            If Me.Tag = "Next" Then
                Call HighlightNextMatch(Me, Me.txtSearch.Value)
                Me.txtSearch.SetFocus
            Else
                
                Call HighlightFirstMatch(Me, Me.txtSearch.Value)
                Me.Tag = "Next" ' Ìåíÿåì ìåòêó, ÷òîáû ñëåäóþùèå íàæàòèÿ âûçûâàëè ñëåäóþùèé ïîèñê
                Me.txtSearch.SetFocus
            End If
        Else
            MsgBox "Ââåäèòå òåêñò äëÿ ïîèñêà.", vbExclamation, "Ïîèñê"
        End If
    End If
End Sub

Private Sub uid_DblClick(Cancel As Integer)
Dim strText As String
    strText = Nz(Me.uid.Value, "ïóñòî")
    Call CopyTextToClipboard(strText)
    
    ' Ïîêàçûâàåì ñîîáùåíèå
    Me.lblNotification.Caption = "UID: '" & strText & "' ñêîïèðîâàí â áóôåð îáìåíó!"
    Me.lblNotification.Visible = True

    ' Ïàóçà ïåðåä î÷èñòêîé
    Dim PauseTime As Single
    PauseTime = Timer + 0.5 ' 1 ñåêóíäà
    Do While Timer < PauseTime
        DoEvents
    Loop

    ' Î÷èùàåì ñîîáùåíèå
    Me.lblNotification.Caption = ""
    Me.lblNotification.Visible = False
    
End Sub

