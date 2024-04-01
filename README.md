> For the purpose of transparency: this little coding exercise was completed in conjunction with a job application to join Fly.io's DevRel team. They rejected my application. They made no claim to this code, so I am sharing it as my intellectual property. I had a lot of fun writing it up, so I hope you enjoy it.

# Building a Microscopic PNG to JPEG converter with Svelte.

## Problem

Perhaps you've been walking in a park or on a trail on a warm summer's day and thought, "What if I wrote a single page PNG to JPEG converter with Svelte..." Well, I haven't either, but it's a more apealing experiment than you may think. The complexities run deeper than surface-level: handling image upload, sorting out image conversion, providing a download method, error handling, and list goes on. If you're like me, you might be imagining it'll take several files, a REST API, and a bunch of fiddling with non-toxic glue. What if I told you we could fit that into <50 lines of readable code with zero dependencies and no server-side code? Let's walk through it.

## Solution

Here's the game plan:
- We initialize a Svelte project.
- We handle file uploads.
- We convert the image to the JPEG format.
- We catch errors.
- We provide a way for users to download the image.
- You take the credit because you walked through the whole process, :).

### Initializing a Svelte project.

This recipe has no dependencies and uses the default SvelteKit configuration, so initializing the project is as easy as `npm create svelte@latest png2jpeg-converter`.

Once you've gotten comfy in your brand-new SvelteKit project, we can make a new page and get started:

```js
<script>
	let error;
	let files;
	let jpeg;
</script>

<center>
	<h2>PNG to JPEG Image Converter</h2>
	<label for="pngFile">Upload a png file:</label>
	<input bind:files type="file" id="pngFile" accept="image/png" />

    <h4>Result:</h4>
	{#if jpeg}
		<img src={jpeg} alt="PNG Converted to JPEG" />
	{/if}
	{#if error}
		<h4 style="color: red;">Error encountered!</h4>
		<code>{error}</code>
	{/if}

	<canvas hidden id="canvas"></canvas>
</center>
```

The majority of this is standard (metadata, data modeling, visual elements), but let's first dig into the `input`.

### Handling file uploads.

```js
<input bind:files type="file" id="pngFile" accept="image/png" />
```

Since it is a file type input it will bind `files` to a [`FileList`](https://developer.mozilla.org/en-US/docs/Web/API/FileList). This allows us to access the data that is uploaded in the form of a [`File`](https://developer.mozilla.org/en-US/docs/Web/API/File):

```js
<script>
	let files;
	...
	$: if (files) {
		let pngFile = files[0];
	}
</script>
```

> Note: File inputs only support uploading a single file if you do not mark them with the `multiple` attribute. It would entirely be possible to adapt the code shared here to support multiple files, but for the sake of brevity we will keep it to one.

### Image conversion.

Wonderful! Now how can we transmorgrify the `File` into JPEG? Javascript has a number of lovely image processing libraries like Sharp or Jimp, but I promised zero-dependencies. This leads us to one of the most fastinating HTML elements: `<canvas>`. Did you catch it in the first code snippet even though it was `hidden`, :D? The `<canvas>` side-quest involves three parts:

1. Being able to write a `File` to the `<canvas>`.
2. Actually writing the `File` to the `<canvas>`.
3. Using the `<canvas>` content as an `<img>`.

You can't write `File`s to a canvas, but you can write [`ImageBitmap`]s(https://developer.mozilla.org/en-US/docs/Web/API/ImageBitmap). We'll use the browser's built-in `createImageBitmap` function:

```js
$: if (files) {
	let pngFile = files[0];
	createImageBitmap(pngFile)
		.then((bitmap) => {
			// Convert to JPEG.
		});
}
```

To complete steps 2-3 we'll finally use our `hidden` canvas. Let's give the conversion it's own function:

```js
function convertToJPEG(bitmap) {
	const canvas = document.getElementById('canvas');
	const ctx = canvas.getContext('2d');
	canvas.width = bitmap.width;
	canvas.height = bitmap.height;
	ctx.drawImage(bitmap, 0, 0);
	return canvas.toDataURL('image/jpeg');
}
```

After getting the canvas from the DOM and accessing a context, we match the `canvas`'s size to the bitmap's to avoid accidentally cropping our image. The next line draws the bitmap to the canvas filling out the perfectly sized canvas.

The last line (`return canvas.toDataURL('image/jpeg');`) introduces us to the magical `toDataURL` method. If you are unfamiliar with Data URLs, [they are a way of encoding data into the URL format](https://developer.mozilla.org/en-US/docs/web/http/basics_of_http/data_urls). The method allows us to specify a MIME type. The browser then converts the `canvas` content to the desired MIME type under the hood. What do we do with this data URL now? `<img>` tags support using data URLs for the `src` attribute. Let's integrate it into our existing code:

```js
<script>
	let files;
	let jpeg;
	...
	$: if (files) {
		let pngFile = files[0];
		createImageBitmap(pngFile)
			.then((bitmap) => {
				jpeg = convertToJPEG(bitmap);
			});
		
		function convertToJPEG(bitmap) {
			...
		}
	}
</script>

<center>
	...
	<h4>Result:</h4>
	{#if jpeg}
		<img src={jpeg} alt="PNG Converted to JPEG" />
	{/if}
	...
</center>
```

### Catching errors.

So what about errors? Assuming the browser and Svelte don't act out, the most likely place for errors to occur is within `createImageBitmap`. Because it returns a promise we can just use `catch` to write errors to `error` and Svelte will take care of the rest.

```js
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
</script>

<center>
	...
	{#if error}
		<h4 style="color: red;">Error encountered!</h4>
		<code>{error}</code>
	{/if}
</center>
```

### Handling downloads.

This is another place where we will take advantage of the built-in capabilities of the browser. We're going to use... *drum roll*. A right-click and "Save As". Although this may not be standard to most tools, we're trying to redefine the user journey and accelerate adoption of modular experience facets. (That's what marketing told me to say, at least.) We will be kind to our users and let them know, though:

```js
{#if jpeg}
	<h4><i>Just right-click the image and click "Save As" to download.</i></h4>
	<img src={jpeg} alt="PNG Converted to JPEG" />
{/if}
```

### Profit!

Just like that we've completed a single page PNG to JPEG converter with Svelte:

```js
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
```

You made it! :champagne: :partying_face:.

## Discussion (optional)

What now? Well, because the codebase is so minimal right now, adding features won't make the single file too unwieldy. Here are some ideas:

- The image conversion code is not limited to PNG or JPEG. Any browser supported image formats can be used for input and output. You could easily add a simple dropdown to select output format, making it an anything-to-anything converter.
- Add a simple caching feature via `File` hashing.
- Beautify the visual-side with some fancy '90s-era styling: `<marquee>`, [cursor-effects](https://github.com/tholman/cursor-effects), `background-color: green;`.
- Add an AI element to attempt to recognize dog pictures (so we can exfiltrate them for the "Awwwwww"s).
- Add watermarks via `<canvas>` [methods](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Drawing_text).
