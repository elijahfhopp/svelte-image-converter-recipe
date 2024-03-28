<script>
	let error;
	let files;
	let jpeg;

	$: if (files) {
		// The "multiple" attribute is required on the input element for multi-upload.
		let pngFile = files[0];
		createImageBitmap(pngFile)
			.then((bitmap) => {
				jpeg = convertToJPEG(bitmap);
			})
			.catch((err) => {
				error = err;
			});
	}

	function convertToJPEG(bitmap) {
		const canvas = document.getElementById('canvas');
		const ctx = canvas.getContext('2d');
		canvas.width = bitmap.width;
		canvas.height = bitmap.height;
		ctx.drawImage(bitmap, 0, 0);
		return canvas.toDataURL('image/jpeg');
	}
</script>

<svelte:head>
	<title>Image Converter</title>
</svelte:head>

<center>
	<canvas hidden id="canvas"></canvas>
	<h2>PNG to JPEG Image Converter</h2>
	<label for="pngFile">Upload a png file:</label>
	<input bind:files type="file" id="pngFile" accept=".png" />
	<h4>Result:</h4>
	{#if jpeg}
		<h4><i>Just right-click the image and click "Save As" to download.</i></h4>
		<img src={jpeg} alt="PNG Converted to JPEG" />
	{/if}
	{#if error}
		<h4 style="color: red;">Error encountered!</h4>
		<code>{error}</code>
	{/if}
</center>
