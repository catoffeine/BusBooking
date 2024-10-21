let preprocessor = 'sass', // Preprocessor (sass, less, styl); 'sass' also work with the Scss syntax in blocks/ folder.
		fileswatch   = 'html,htm,txt,json,md,woff2' // List of files extensions for watching & hard reload

import pkg from 'gulp'
const { gulp, src, dest, parallel, series, watch } = pkg;

// import browserSync   from 'browser-sync'
// import bssi          from 'browsersync-ssi'
// import ssi           from 'ssi'
// import webpackStream from 'webpack-stream'
// import webpack       from 'webpack'
// import TerserPlugin  from 'terser-webpack-plugin'
import gulpSass      from 'gulp-sass'
import dartSass      from 'sass'
import sassglob      from 'gulp-sass-glob'
const  sass          = gulpSass(dartSass)
// import less          from 'gulp-less'
// import lessglob      from 'gulp-less-glob'
// import styl          from 'gulp-stylus'
// import stylglob      from 'gulp-noop'
import postCss       from 'gulp-postcss'
import cssnano       from 'cssnano'
import autoprefixer  from 'autoprefixer'
import imagemin      from 'gulp-imagemin'
import changed       from 'gulp-changed'
import concat        from 'gulp-concat'
// import rsync         from 'gulp-rsync'
import {deleteAsync} from 'del'

// function browsersync() {
// 	browserSync.init({
// 		server: {
// 			baseDir: 'app/',
// 			middleware: bssi({ baseDir: 'app/', ext: '.html' })
// 		},
// 		ghostMode: { clicks: false },
// 		notify: false,
// 		online: true,
// 		// tunnel: 'yousutename', // Attempt to use the URL https://yousutename.loca.lt
// 	})
// }

// function scripts() {
// 	return src(['app/js/*.js', '!app/js/*.min.js'])
// 		.pipe(webpackStream({
// 			mode: 'production',
// 			performance: { hints: false },
// 			plugins: [
// 				new webpack.ProvidePlugin({ $: 'jquery', jQuery: 'jquery', 'window.jQuery': 'jquery' }), // jQuery (npm i jquery)
// 			],
// 			module: {
// 				rules: [
// 					{
// 						test: /\.m?js$/,
// 						exclude: /(node_modules)/,
// 						use: {
// 							loader: 'babel-loader',
// 							options: {
// 								presets: ['@babel/preset-env'],
// 								plugins: ['babel-plugin-root-import']
// 							}
// 						}
// 					}
// 				]
// 			},
// 			optimization: {
// 				minimize: true,
// 				minimizer: [
// 					new TerserPlugin({
// 						terserOptions: { format: { comments: false } },
// 						extractComments: false
// 					})
// 				]
// 			},
// 		}, webpack)).on('error', (err) => {
// 			this.emit('end')
// 		})
// 		.pipe(concat('app.min.js'))
// 		.pipe(dest('app/js'))
// }

function styles() {
    return src([`app/styles/*.*`, `!app/styles/_*.*`])
    .pipe(eval(`${preprocessor}glob`)())
    .pipe(eval(preprocessor)({ 'include css': true }))
    .pipe(postCss([
        autoprefixer({ grid: 'autoplace' }),
        cssnano({ preset: ['default', { discardComments: { removeAll: true } }] })
    ]))
    .pipe(concat('styles.min.css'))
    .pipe(dest('../BookingService/static_files/'));
}

function img_minimize() {
    return src(['app/images/**/*', '!app/images/dist/**/*'])
		.pipe(changed('app/images/dist'))
		.pipe(imagemin())
		.pipe(dest('app/images/dist'));
}

function copy_images() {
    return src('app/images/dist/**/*')
    .pipe(dest('../BookingService/static_files/images/'));
}

function copy_fonts() {
    return src('app/fonts/*')
    .pipe(dest('../BookingService/static_files/fonts/'));
}

function copy_scripts() {
    return src(['app/js/**/*', 'app/js/*_.*'])
    .pipe(dest('../BookingService/static_files/js/'));
}

async function clean_files() {
	await deleteAsync('../BookingService/static_files/**/*', { force: true });
    await deleteAsync('app/images/dist', { force: true });
}

// export { scripts, styles, images, deploy }
// export let assets = series(scripts, styles, images)
// export let build = series(cleandist, images, scripts, styles, buildcopy, buildhtml)

function startwatch() {
    watch('app/styles/**/*', { usePolling: true }, styles);
    watch('app/images/**/*', { usePolling: true }, series(img_minimize, copy_images));
    watch('app/fonts/**/*', { usePolling: true }, copy_fonts);
    watch('app/js/**/*', { usePolling: true }, copy_scripts);
}

export let build = series(clean_files, styles, img_minimize, copy_images, copy_fonts, copy_scripts);
export let clean = clean_files;
export let start_watch = series(build, startwatch);

// export default series(scripts, styles, images, parallel(browsersync, startwatch))
