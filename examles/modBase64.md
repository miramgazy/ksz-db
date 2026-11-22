Attribute VB_Name = "modBase64"
Option Compare Database
Option Explicit

Public Function Base64Encode(inData As String) As String
    On Error GoTo ErrHandler
    Dim arrData() As Byte
    arrData = StrConv(inData, vbFromUnicode)
    
    Dim objXML As Object
    Dim objNode As Object
    Set objXML = CreateObject("MSXML2.DOMDocument")
    Set objNode = objXML.createElement("b64")
    
    objNode.DataType = "bin.base64"
    objNode.nodeTypedValue = arrData
    
    Base64Encode = Replace(objNode.Text, vbLf, "")
    
    Set objNode = Nothing
    Set objXML = Nothing
    Exit Function
    
ErrHandler:
    Base64Encode = ""
End Function

Public Function Base64Decode(base64String As String) As String
    On Error GoTo ErrHandler
    Dim objXML As Object
    Dim objNode As Object
    Set objXML = CreateObject("MSXML2.DOMDocument")
    Set objNode = objXML.createElement("b64")
    
    objNode.DataType = "bin.base64"
    objNode.Text = base64String
    
    Base64Decode = StrConv(objNode.nodeTypedValue, vbUnicode)
    
    Set objNode = Nothing
    Set objXML = Nothing
    Exit Function
    
ErrHandler:
    Base64Decode = ""
End Function

