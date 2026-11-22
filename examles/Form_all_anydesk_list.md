Option Compare Database
Option Explicit

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


Private Sub cmdClose_Click()
DoCmd.Close
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



Private Sub Form_Open(Cancel As Integer)
DoCmd.Maximize
End Sub

Private Sub select_iikoRosta_AfterUpdate()
Me.Refresh
End Sub
Private Sub iikoVersion_DblClick(Cancel As Integer)
Dim strText As String
    strText = Nz(Me.linkYa.Value, "ïóñòî")
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
    link = "https://miramgazy.github.io/front-bg-creator/crmlink.html?text=" & Me.crmid
    Application.FollowHyperlink link
End Sub

Private Sub select_iikoRosta_Click()
If IsNull(Me.select_iikoRosta) Then
Me.FilterOn = False

Else
Me.Filter = "iiko_rosta=" & Me.select_iikoRosta
Me.FilterOn = True
End If
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
    strText = Nz(Me.sysadminPass.Value, "ïóñòî")
    Call CopyTextToClipboard(strText)
    
     ' Ïîêàçûâàåì ñîîáùåíèå
    Me.lblNotification.Caption = "Ïàðîëü ñèñÀäìèíà: '" & strText & "' ñêîïèðîâàí â áóôåð îáìåíó!"
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

Private Sub txtOpen_Click()
  Dim anydeskID As String
    Dim anydeskPassword As String
    Dim shellCommand As String
    Dim fullURL As String
    Dim anydeskPath As String
    
    ' Óêàçûâàåì ïóòü ê AnyDesk
    anydeskPath = """C:\Program Files (x86)\AnyDesk\AnyDesk.exe"""

    ' Ïðîâåðÿåì, çàïîëíåíî ëè ïîëå anyId
    If IsNull(Me!anyID) Or Trim(Me!anyID) = "" Then
        MsgBox "Ïîëå anyId ïóñòîå. Ïîæàëóéñòà, óêàæèòå ID AnyDesk.", vbExclamation
        Exit Sub
    End If

    ' Ïîëó÷àåì çíà÷åíèå ID (ïîääåðæèâàåò òåêñò è öèôðû)
    anydeskID = Me!anyID.Value

    ' Ïðîâåðÿåì, çàïîëíåíî ëè ïîëå anyPassword
    If Not IsNull(Me!anyPassword) And Trim(Me!anyPassword) <> "" Then
        anydeskPassword = Me!anyPassword.Value
        ' Ôîðìèðóåì URL äëÿ áðàóçåðà
        fullURL = "clearbat://anydesk@" & anydeskID & ":" & anydeskPassword
        shellCommand = "rundll32.exe url.dll,FileProtocolHandler " & fullURL
    Else
        ' Åñëè ïàðîëü îòñóòñòâóåò, çàïóñêàåì AnyDesk íàïðÿìóþ
        shellCommand = anydeskPath & " " & anydeskID
    End If

    ' Çàïóñê êîìàíäû
    Shell shellCommand, vbNormalFocus
End Sub

Private Sub Ïîëå196_DblClick(Cancel As Integer)
    Dim anydeskPath As String
    Dim anydeskID As String
    Dim anydeskPassword As String
    Dim shellCommand As String
    
    ' Ïóòü ê ôàéëó AnyDesk
    anydeskPath = """C:\Program Files (x86)\AnyDesk\AnyDesk.exe"""
    
    ' Ïðîâåðÿåì, ñóùåñòâóåò ëè ïîëå anyId è ñîäåðæèò ëè îíî çíà÷åíèå
    If IsNull(Me!anyID) Or Me!anyID = "" Then
        MsgBox "Ïîëå anyId ïóñòîå. Ïîæàëóéñòà, óêàæèòå ID AnyDesk.", vbExclamation
        Exit Sub
    End If
    
    ' Ïîëó÷àåì çíà÷åíèå ïîëÿ anyId
    anydeskID = Me!anyID.Value
    
    ' Ïðîâåðÿåì, ñóùåñòâóåò ëè ïîëå anyPassword è ñîäåðæèò ëè îíî çíà÷åíèå
    If Not IsNull(Me!anyPassword) Or Me!anyPassword <> "" Then
        ' Åñëè ïàðîëü óêàçàí, äîáàâëÿåì åãî â êîìàíäó
        anydeskPassword = Me!anyPassword.Value
        shellCommand = anydeskPath & " " & anydeskID & " --with-password " & anydeskPassword
    Else
        ' Åñëè ïàðîëü íå óêàçàí, çàïóñêàåì òîëüêî ñ ID
        shellCommand = anydeskPath & " " & anydeskID
    End If
    
    ' Çàïóñêàåì AnyDesk
    Shell shellCommand, vbNormalFocus
End Sub
