<?php

require '../utils.php';
class User
{
    public $username;
    public $isAdmin;

    public function __construct($username, $isAdmin)
    {
        $this->username = $username;
        $this->isAdmin = $isAdmin;
    }

    $serializedUserData = $ COOKIE['user_data']; 
    $userData = unserialize(sanitize_for_unserialize($serializedUserData));  
    if ($userData instanceof User) {
        if ($userData->isAdmin) {
            echo "Welcome, Admin " . $userData->username . "!";
        } else {
            echo "Welcome, " . $userData->username . "!";
        }
    } else {
        echo "<h1>Error: Invalid user data</h1>";
    }
}
?>
