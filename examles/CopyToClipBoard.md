Attribute VB_Name = "CopyToClipBoard"
Option Explicit

Private Declare PtrSafe Function OpenClipboard Lib "user32" (ByVal hWnd As LongPtr) As Long
Private Declare PtrSafe Function EmptyClipboard Lib "user32" () As Long
Private Declare PtrSafe Function CloseClipboard Lib "user32" () As Long
Private Declare PtrSafe Function SetClipboardData Lib "user32" (ByVal uFormat As Long, ByVal hMem As LongPtr) As LongPtr
Private Declare PtrSafe Function GlobalAlloc Lib "kernel32" (ByVal wFlags As Long, ByVal dwBytes As Long) As LongPtr
Private Declare PtrSafe Function GlobalLock Lib "kernel32" (ByVal hMem As LongPtr) As LongPtr
Private Declare PtrSafe Function GlobalUnlock Lib "kernel32" (ByVal hMem As Long) As Long
Private Declare PtrSafe Function lstrcpy Lib "kernel32" (ByVal lpString1 As LongPtr, ByVal lpString2 As String) As LongPtr

Private Const GHND = &H42
Private Const CF_TEXT = 1

Public Sub CopyTextToClipboard(strText As String)
    Dim hGlobalMemory As LongPtr
    Dim lpMemory As LongPtr

    If OpenClipboard(0&) Then
        EmptyClipboard
        hGlobalMemory = GlobalAlloc(GHND, Len(strText) + 1)
        lpMemory = GlobalLock(hGlobalMemory)
        lstrcpy lpMemory, strText
        GlobalUnlock hGlobalMemory
        SetClipboardData CF_TEXT, hGlobalMemory
        CloseClipboard
    End If
End Sub

