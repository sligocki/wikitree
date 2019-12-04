<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang="en" dir="ltr" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
<?php
	preg_match("@apps/(\S+)/@", $_SERVER['PHP_SELF'], $m);
	$apps_user = $m[1];
?>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<meta name="robots" content="noindex, nofollow" />
	<title>WikiTree Apps from User <?php echo $apps_user ?></title>

	<!-- Include main WikiTree.com CSS -->
	<link rel="stylesheet" href="https://www.wikitree.com/css/main-new.css?2" type="text/css" />
</head>

<body>
<?php include "/apps/header.htm"; ?>
<div id="HEADLINE">
	<h1>WikiTree Apps from User <?php echo $apps_user; ?></h1>
</div>

<div id="CONTENT" class="MISC-PAGE">

	<h2>WikiTree Apps from User <?php echo $apps_user; ?></h2>

</div><!-- eo CONTENT -->

<?php include "/apps/footer.htm"; ?>
</body>
</html>

