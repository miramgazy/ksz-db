VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "Form_Company Details"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Compare Database

Private Sub addAnydeskLounch_Click()

End Sub

Private Sub backOffice_Click()
    Dim serverAddress As String
    Dim portN As String
    Dim sysAdminName As String
    Dim sysadminPassFromDB As String
    Dim plainPass As String
    Dim rawParams As String
    Dim finalBase64 As String
    Dim fullURL As String
    Dim shellCommand As String
    Dim re As Object

    ' 1. �������� ���������� �����
    If IsNull(Me!server_name) Or Trim(Me!server_name) = "" Then
        MsgBox "����� ������� �� ������", vbExclamation
        Exit Sub
    End If

    If IsNull(Me!portN) Or Trim(Me!portN) = "" Then
        MsgBox "����� ����� �� ������", vbExclamation
        Exit Sub
    End If

    If IsNull(Me!sysadminlogin) Or Trim(Me!sysadminlogin) = "" Then
        MsgBox "����� �� ������", vbExclamation
        Exit Sub
    End If

    If IsNull(Me!sysadminPass) Or Trim(Me!sysadminPass) = "" Then
        MsgBox "������ �� ������", vbExclamation
        Exit Sub
    End If

    ' 2. �������� ��������
    serverAddress = Trim(Me!server_name)
    portN = Trim(Me!portN)
    sysAdminName = Trim(Me!sysadminlogin)
    sysadminPassFromDB = Nz(Me!sysadminPass, "")

    ' 3. ����������� ������ ��� ��������� ������� ������
    ' ��������� �������� ���������� ����������, ���� �� �� �������, � ����� ������� ������
    Set re = CreateObject("VBScript.RegExp")
    re.Pattern = "^[A-Za-z0-9+/=]+$"
    
    If re.Test(sysadminPassFromDB) Then
        On Error Resume Next
        plainPass = Base64Decode(sysadminPassFromDB)
        If Err.Number <> 0 Or plainPass = "" Then
            plainPass = sysadminPassFromDB
        End If
        On Error GoTo 0
    Else
        plainPass = sysadminPassFromDB
    End If

    ' 4. ������������ ������ ���������� (V2)
    ' �������� �����: ?type=iiko?url=host:port?login=user?password=pass
    rawParams = "?type=iiko?url=" & serverAddress & ":" & portN & _
                "?login=" & sysAdminName & "?password=" & plainPass

    ' 5. ������ ����������� ������
    ' ��� ������ ���������� ������������ � ���� Base64 ����
    finalBase64 = Base64Encode(rawParams)

    ' 6. ������ ��������� URL
    ' ����� ��������� V2: ���� ���� ����� ��������� � ���� � �����
    fullURL = "clearbat:/" & finalBase64 & "?encode=full"

    ' 7. ������
    ' ���������� ������� ������� ��� ������������ ���� � Windows
    shellCommand = "rundll32.exe url.dll,FileProtocolHandler """ & fullURL & """"

    If Shell(shellCommand, vbNormalFocus) = 0 Then
        MsgBox "������ �������. ��������� ��������� ClearBat.", vbCritical
    End If

    ' 8. ������ � ������� � ������������
    Call CopyTextToClipboard(plainPass)
    
    Me.lblNotification.Caption = "������ V2... ������ ���������� � �����."
    Me.lblNotification.Visible = True

    ' �������� �����
    Dim PauseTime As Single
    PauseTime = Timer + 0.8
    Do While Timer < PauseTime
        DoEvents
    Loop

    Me.lblNotification.Visible = False
    Me.lblNotification.Caption = ""
End Sub

Private Sub cabiten_Click()

End Sub

Private Sub companyN_Click()

    Dim link As String
    Dim browser As String
    Dim strText As String
    
    strText = Nz(Me.uid.Value, "�����")
    Call CopyTextToClipboard(strText)

    link = "https://pp.iiko.ru/ru/cabinet/clients.html"

    ' ������� 1 � ��������� ��� �������� ������������
    browser = Environ("LOCALAPPDATA") & _
              "\Yandex\YandexBrowser\Application\browser.exe"

    ' ������� 2 � ��������� ��� ���� �������������
    If Dir(browser) = "" Then
        browser = "C:\Program Files\Yandex\YandexBrowser\Application\browser.exe"
    End If

    ' ������� 3 � Program Files (x86)
    If Dir(browser) = "" Then
        browser = "C:\Program Files (x86)\Yandex\YandexBrowser\Application\browser.exe"
    End If

    If Dir(browser) = "" Then
        MsgBox "������ ������� �� ������.", vbExclamation
        Exit Sub
    End If

    Shell """" & browser & """ """ & link & """", vbNormalFocus

End Sub

Private Sub crmId_DblClick(Cancel As Integer)
On Error Resume Next
Dim strText As String
    strText = Nz(Me.crmid.Value, "�����")
    Call CopyTextToClipboard(strText)
    
    ' ���������� ���������
    Me.lblNotification.Caption = "CRMID: '" & strText & "' ���������� � ����� ������!"
    Me.lblNotification.Visible = True

    ' ����� ����� ��������
    Dim PauseTime As Single
    PauseTime = Timer + 0.5 ' 1 �������
    Do While Timer < PauseTime
        DoEvents
    Loop

    ' ������� ���������
    Me.lblNotification.Caption = ""
    Me.lblNotification.Visible = False
    
End Sub

Private Sub iconNewAnydesk_Click()
Dim strSQL As String
            Set cn = CurrentProject.Connection
            strSQL = "INSERT INTO  anydesk_list ([company_id])VALUES " _
            & "('" & Me.id & "');"
            cn.Execute (strSQL)
 Me.Refresh
End Sub

Private Sub iikoWeb_Click()
    Dim link As String
    Dim strText As String
    Dim decodedText As String
    Dim PauseTime As Single
    
    link = Me.iikoWeblink & "/navigator/index.html#/auth/login"
    Application.FollowHyperlink link
    
' ����������� ������
 
    strText = Nz(Me.sysadminPass, "�����")
    If InStr(strText, "=") > 0 Or strText Like "*[A-Za-z0-9+/=]*" Then
        On Error Resume Next
        decodedText = DecodeBase64(strText)
        If Err.Number <> 0 Or decodedText = "" Then
            decodedText = strText
        End If
        On Error GoTo 0
    Else
        decodedText = strText
    End If
    Call CopyTextToClipboard(decodedText)
    
     ' ���������� ���������
    Me.lblNotification.Caption = "������ ���������: '" & decodedText & "' ���������� � ����� ������!"
    Me.lblNotification.Visible = True

    ' ����� ����� ��������
    PauseTime = Timer + 0.7 ' 1 �������
    Do While Timer < PauseTime
        DoEvents
    Loop

    ' ������� ���������
    Me.lblNotification.Caption = ""
    Me.lblNotification.Visible = False
End Sub

Private Sub insertDataCB_Click()
    On Error GoTo ErrHandler

    Dim conn As Object
    Dim rs As Object
    Dim cmd As Object
    Dim dbPath As String
    Dim sql As String
    Dim newRevision As Long
    Dim daoDB As DAO.Database
    Dim rsSettings As DAO.Recordset
    Dim pwd As String

    ' --- 1. �������� ���� � ���� ---
    Set daoDB = CurrentDb
    Set rsSettings = daoDB.OpenRecordset("SELECT ClearBatDBPath FROM Settings WHERE ID = 1", dbOpenSnapshot)

    If rsSettings.EOF Then
        rsSettings.Close
        MsgBox "���� � ���� ������ ClearBat ����������� � ����������.", vbExclamation, "������ ������������"
        DoCmd.OpenForm "frmStartup", , , , , acDialog
        Exit Sub
    End If

    dbPath = Nz(rsSettings!clearBatDBPath, "")
    rsSettings.Close

    If Dir(dbPath) = "" Then
        MsgBox "���� ���� ������ �� ������ �� ����:" & vbCrLf & dbPath, vbCritical, "���� �� ������"
        Exit Sub
    End If

    ' --- 2. �������� ������ (�������� ��� ���?) ---
    pwd = Nz(Me.sysadminPass, "")

    If pwd = "" Then
        MsgBox "������ �� ����� ���� ������!", vbExclamation
        Exit Sub
    End If

    ' ������ ��������: ������� ������������ � ������������ �������.
    ' ���� ��������� ������, ������ � ���� ��� ��� Base64.
    ' ���� ��� (��� ������) � ������ ������ ������ � �������� ����.
    Dim decoded As String
    Dim reEncoded As String
    
    decoded = Base64Decode(pwd)
    reEncoded = Base64Encode(decoded)
    
    ' ���������� ��������� ����� � ����������� �������������
    ' ���� ��� �� �����, ������ ������ �� ��� ���������� ���������
    If pwd <> reEncoded Then
        MsgBox "������ ������ �� ����������!" & vbCrLf & _
               "������ �� ����� ���� ��������� � ���� � �������� ����." & vbCrLf & _
               "����������, ����������� ������� ���������� ����� �����������.", vbCritical, "������ ������������"
        Exit Sub
    End If

    ' --- 3. ����������� � SQLITE ---
    Set conn = CreateObject("ADODB.Connection")
    conn.Open "Driver={SQLite3 ODBC Driver};Database=" & dbPath & ";"

    ' --- 4. ������ REVISION ---
    Set rs = CreateObject("ADODB.Recordset")
    rs.Open "SELECT MAX(revision) AS maxRev FROM Entities;", conn

    If Not rs.EOF Then
        newRevision = Nz(rs.Fields("maxRev").Value, 0) + 1
    Else
        newRevision = 1
    End If
    rs.Close

    ' --- 5. ������������ SQL (� ������� �� �������) ---
    sql = "INSERT INTO Entities (name, type, folder, ip, port, login, password, deleted, revision) " & _
          "VALUES (" & _
            "'" & Replace(Nz(Me.place_name, ""), "'", "''") & "', " & _
            "'iikoOffice', " & _
            "NULL, " & _
            "'" & Replace(Nz(Me.server_name, ""), "'", "''") & "', " & _
            "'" & Replace(Nz(Me.portN, ""), "'", "''") & "', " & _
            "'" & Replace(Nz(Me.sysadminlogin, ""), "'", "''") & "', " & _
            "'" & pwd & "', " & _
            "'False', " & newRevision & ");"

    ' --- 6. ���������� ---
    Set cmd = CreateObject("ADODB.Command")
    cmd.ActiveConnection = conn
    cmd.CommandText = sql
    cmd.Execute

    MsgBox "������ ������� ���������!" & vbCrLf & _
           "Revision: " & newRevision, vbInformation, "������"

Cleanup:
    On Error Resume Next
    If Not rs Is Nothing Then If rs.state = 1 Then rs.Close
    If Not conn Is Nothing Then If conn.state = 1 Then conn.Close
    Set rs = Nothing: Set cmd = Nothing: Set conn = Nothing
    Exit Sub

ErrHandler:
    MsgBox "������ ��� ����������: " & Err.description, vbCritical, "����������� ������"
    Resume Cleanup
End Sub
Private Sub license_updater_Click()
 Dim serverAddress As String
    Dim portN As String
    Dim sysAdminName As String
    Dim sysadminPassFromDB As String
    Dim plainPass As String
    Dim rawParams As String
    Dim fullURL As String
    Dim shellCommand As String
    Dim re As Object

    ' 1. �������� ���������� �����
    If IsNull(Me!server_name) Or Trim(Me!server_name) = "" Then
        MsgBox "����� ������� �� ������", vbExclamation
        Exit Sub
    End If

    If IsNull(Me!portN) Or Trim(Me!portN) = "" Then
        MsgBox "����� ����� �� ������", vbExclamation
        Exit Sub
    End If

    If IsNull(Me!sysadminlogin) Or Trim(Me!sysadminlogin) = "" Then
        MsgBox "����� �� ������", vbExclamation
        Exit Sub
    End If

    If IsNull(Me!sysadminPass) Or Trim(Me!sysadminPass) = "" Then
        MsgBox "������ �� ������", vbExclamation
        Exit Sub
    End If

    ' 2. �������� ��������
    serverAddress = Trim(Me!server_name)
    portN = Trim(Me!portN)
    sysAdminName = Trim(Me!sysadminlogin)
    sysadminPassFromDB = Nz(Me!sysadminPass, "")

    ' 3. ����������� ������
    Set re = CreateObject("VBScript.RegExp")
    re.Pattern = "^[A-Za-z0-9+/=]+$"
    
    If re.Test(sysadminPassFromDB) Then
        On Error Resume Next
        plainPass = Base64Decode(sysadminPassFromDB)
        If Err.Number <> 0 Or plainPass = "" Then
            plainPass = sysadminPassFromDB
        End If
        On Error GoTo 0
    Else
        plainPass = sysadminPassFromDB
    End If

    ' 4. ������������ ������ ���������� ��� ��������
    ' ������: clearbat:/type=license?url=host:port?login=user?password=pass
    fullURL = "clearbat:/type=license?url=" & serverAddress & ":" & portN & _
              "?login=" & sysAdminName & "?password=" & plainPass

    ' 5. ������
    ' ���������� ShellExecute ����� rundll32
    shellCommand = "rundll32.exe url.dll,FileProtocolHandler """ & fullURL & """"

    If Shell(shellCommand, vbNormalFocus) = 0 Then
        MsgBox "������ �������. ��������� ��������� ClearBat.", vbCritical
    Else
        ' 6. ����������� �� ������
        Me.lblNotification.Caption = "������ �� ���������� �������� ���������..."
        Me.lblNotification.Visible = True

        ' �������� �����
        Dim PauseTime As Single
        PauseTime = Timer + 1.5
        Do While Timer < PauseTime
            DoEvents
        Loop

        Me.lblNotification.Visible = False
    End If
End Sub

Private Sub server_name_DblClick(Cancel As Integer)
  Dim strText As String
    strText = Nz(Me.server_name.Value, "�����")
    Call CopyTextToClipboard(strText)
    
    ' ���������� ���������
    Me.lblNotification.Caption = "����� �������: '" & strText & "' ���������� � ����� ������!"
    Me.lblNotification.Visible = True

    ' ����� ����� ��������
    Dim PauseTime As Single
    PauseTime = Timer + 0.7 ' 1 �������
    Do While Timer < PauseTime
        DoEvents
    Loop

    ' ������� ���������
    Me.lblNotification.Caption = ""
    Me.lblNotification.Visible = False
End Sub

Private Sub sysadminlogin_DblClick(Cancel As Integer)
Dim strText As String
    strText = Nz(Me.sysadminlogin.Value, "�����")
    Call CopyTextToClipboard(strText)
    
    ' ���������� ���������
    Me.lblNotification.Caption = "Login ���������: '" & strText & "' ���������� � ����� ������!"
    Me.lblNotification.Visible = True

    ' ����� ����� ��������
    Dim PauseTime As Single
    PauseTime = Timer + 0.7 ' 1 �������
    Do While Timer < PauseTime
        DoEvents
    Loop

    ' ������� ���������
    Me.lblNotification.Caption = ""
    Me.lblNotification.Visible = False
    
End Sub

Private Sub sysadminPass_DblClick(Cancel As Integer)
    Dim link As String
    Dim strText As String
    Dim decodedText As String
    Dim PauseTime As Single
    
    strText = Nz(Me.sysadminPass.Value, "�����")
    
    If InStr(strText, "=") > 0 Or strText Like "*[A-Za-z0-9+/=]*" Then
        On Error Resume Next
        decodedText = DecodeBase64(strText)
        If Err.Number <> 0 Or decodedText = "" Then
            decodedText = strText
        End If
        On Error GoTo 0
    Else
        decodedText = strText
    End If
    
    Call CopyTextToClipboard(decodedText)
    
     ' ���������� ���������
    Me.lblNotification.Caption = "������ ���������: '" & decodedText & "' ���������� � ����� ������!"
    Me.lblNotification.Visible = True

    ' ����� ����� ��������
    PauseTime = Timer + 0.7 ' 1 �������
    Do While Timer < PauseTime
        DoEvents
    Loop

    ' ������� ���������
    Me.lblNotification.Caption = ""
    Me.lblNotification.Visible = False
    
End Sub

Private Sub uid_DblClick(Cancel As Integer)
On Error Resume Next
Dim strText As String
    strText = Nz(Me.uid.Value, "�����")
    Call CopyTextToClipboard(strText)
    
    ' ���������� ���������
    Me.lblNotification.Caption = "UID: '" & strText & "' ���������� � ����� ������!"
    Me.lblNotification.Visible = True

    ' ����� ����� ��������
    Dim PauseTime As Single
    PauseTime = Timer + 0.5 ' 1 �������
    Do While Timer < PauseTime
        DoEvents
    Loop

    ' ������� ���������
    Me.lblNotification.Caption = ""
    Me.lblNotification.Visible = False
    
End Sub

Private Sub ������645_Click()
DoCmd.Close
End Sub

Private Sub �������594_Click()
 Dim strSQL As String
            Set cn = CurrentProject.Connection
            strSQL = "INSERT INTO  anydesk_list ([company_id])VALUES " _
            & "('" & Me.id & "');"
            cn.Execute (strSQL)
 Me.Refresh
End Sub

Private Sub �������671_Click()
Dim link As String
    Dim strText As String
    Dim decodedText As String
    Dim PauseTime As Single
    
    link = "https://" & Me.server_name & ":443/resto"
    Application.FollowHyperlink link
    
' ����������� ������
    strText = Nz(Me.sysadminPass.Value, "�����")
    
    If InStr(strText, "=") > 0 Or strText Like "*[A-Za-z0-9+/=]*" Then
        On Error Resume Next
        decodedText = DecodeBase64(strText)
        If Err.Number <> 0 Or decodedText = "" Then
            decodedText = strText
        End If
        On Error GoTo 0
    Else
        decodedText = strText
    End If
    
   Call CopyTextToClipboard(decodedText)
    
     ' ���������� ���������
    Me.lblNotification.Caption = "������ ���������: '" & decodedText & "' ���������� � ����� ������!"
    Me.lblNotification.Visible = True

    ' ����� ����� ��������
    PauseTime = Timer + 0.7 ' 1 �������
    Do While Timer < PauseTime
        DoEvents
    Loop

    ' ������� ���������
    Me.lblNotification.Caption = ""
    Me.lblNotification.Visible = False
End Sub
