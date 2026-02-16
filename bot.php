<?php

file_put_contents("log.txt", "CALLED " . date("H:i:s") . "\n", FILE_APPEND);

echo "OK";
