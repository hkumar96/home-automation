<?php
include 'client.php';
$message = "SET STATS\n";
if (isset($_POST["item"])) {
  $message .= "item: ".$_POST["item"]."\n";
}
if (isset($_POST["id"])) {
  $message .= "id: ".$_POST["id"]."\n";
}
if (isset($_POST["state"])) {
  $message .= "state: ".$_POST["state"]."\n";
}
if (isset($_POST["value"])) {
  $message .= "value: ".$_POST["value"]."\n";
}
// echo $message;
//Send the message to the server
if( ! socket_send ( $sock , $message , strlen($message) , 0))
{
    $errorcode = socket_last_error();
    $errormsg = socket_strerror($errorcode);

    die("Could not send data: [$errorcode] $errormsg \n");
}

// echo "Message send successfully \n";

//Now receive reply from server
if(socket_recv ( $sock , $buf , 2045 , MSG_WAITALL ) === FALSE)
{
    $errorcode = socket_last_error();
    $errormsg = socket_strerror($errorcode);

    die("Could not receive data: [$errorcode] $errormsg \n");
}

//print the received message
socket_shutdown($sock,2);
socket_close($sock);
echo $buf;
// $file_source = "home_states.json";
// $json_data = file_get_contents($file_source);
// echo $json_data;

 ?>
