<?php
function getAppHost()
{
  $root = "http://" . $_SERVER['HTTP_HOST'];
  $root .= str_replace(basename($_SERVER['SCRIPT_NAME']), "", $_SERVER['SCRIPT_NAME']);
  return $root;
}
$phpmyadmin = 'http://localhost:8002/';
?>

<!DOCTYPE html>
<html lang="en">

<head>
  <title>Docker-PHP-7 Stack</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
</head>

<body>

  <div class="container-fluid">
    <div class="row">
      <a style="margin:5px;" class="col-md-2 btn btn-success" target="_blank" href="<?php echo $phpmyadmin ?>">phpMyAdmin</a>
    </div>

    <div class="row">
      <?php
      $path    = dirname(__FILE__);
      $aFolder = scandir($path);
      $exclued = ['.', '..', 'Dockerfile', 'index.php', 'dump', 'apache2'];
      foreach ($aFolder as $value)
      {
        if (!in_array($value, $exclued))
        {
          $url = $base_url . '/' . $value;
      ?>
          <a style="margin:5px;" class="col-md-2 btn btn-primary" href="<?php echo $url; ?>"><?php echo $value; ?></a>
      <?php
        }
      }
      ?>
    </div>

  </div>

</body>

</html>
