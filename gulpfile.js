// Import
var gulp = require('gulp');
var autoprefixer = require('gulp-autoprefixer');
var minify = require('gulp-clean-css');
var plumber = require('gulp-plumber');
var rename = require('gulp-rename');
var uglify = require('gulp-uglify');
var concat = require('gulp-concat');
var sourcemaps = require('gulp-sourcemaps');
var htmlmin = require('gulp-htmlmin');
var fileVer = require('gulp-version-append');
var rimraf = require('rimraf');
var runSequence = require('run-sequence');
var browserSync = require('browser-sync').create();
var historyApiFallback = require('connect-history-api-fallback');
var inlinesource = require('gulp-inline-source');

// Globals
var paths = {
    styles: {
        source: 'src/styles/*.css',
        vendor: [
        ],
        destination: 'dist/css'
    },
    fonts: {
        source: [
            'src/fonts/**/*'
        ],        
        destination: 'dist/fonts'
    },
    js: {
        source: 'src/scripts/**/*.js',
        vendor: [
            'node_modules/zepto/dist/zepto.min.js'
        ],
        destination: 'dist/js'
    },
    html: {
        source: [
            'src/**/*.html'
        ],
        destination: 'dist'
    },
    img: {
        source: 'src/assets',
        destination: 'dist/assets'
    }
};

// clean JS
gulp.task('clean:js', function (cb) {
    return rimraf(paths.js.destination, cb);
});

// clean CSS
gulp.task('clean:css', function (cb) {
    return rimraf(paths.styles.destination, cb);
});

// copy images
gulp.task('copy:img', function () {
    return gulp.src(paths.img.source + '/**', {
            base: paths.img.source
        })
        .pipe(gulp.dest(paths.img.destination));
});

// copy fonts
gulp.task('copy:fonts', function () {
    return gulp.src(paths.fonts.source)
        .pipe(gulp.dest(paths.fonts.destination));
});

// vendor CSS
gulp.task('vendor:css', function () {
    return gulp.src(paths.styles.vendor)
        .pipe(plumber())
        .pipe(concat('vendor.css'))
        .pipe(gulp.dest(paths.styles.destination));
});

// bundle CSS
gulp.task('bundle:css', function () {
    return gulp.src(paths.styles.source)
        .pipe(plumber())
        .pipe(autoprefixer({
            cascade: false
        }))
        .pipe(minify())
        .pipe(concat('bundle.css'))
        .pipe(rename(function (path) {
            path.extname = '.min.css';
        }))
        .pipe(gulp.dest(paths.styles.destination));
});

// vendor JS
gulp.task('vendor:js', function () {
    return gulp.src(paths.js.vendor)
        .pipe(plumber())
        .pipe(concat('vendor.js'))
        .pipe(gulp.dest(paths.js.destination));
});

// bundle JS
gulp.task('bundle_dev:js', function () {
    var source = [paths.js.source];

    return gulp.src(source)
        .pipe(plumber())
        //.pipe(sourcemaps.init())
        .pipe(concat('bundle.js'))
        .pipe(uglify())
        //.pipe(sourcemaps.write())
        .pipe(gulp.dest(paths.js.destination));
});

// minify html 
gulp.task('html', function () {
    return gulp.src(paths.html.source)
        //.pipe(fileVer(['html', 'js', 'css']))
        .pipe(htmlmin({
            collapseWhitespace: true,
            removeComments: true
        }))
        .pipe(gulp.dest(paths.html.destination));
});

// watch
gulp.task('css-watch', ['bundle:css'], function (done) {
    browserSync.reload();
    done();
});

gulp.task('js-watch', ['bundle_dev:js'], function (done) {
    browserSync.reload();
    done();
});

gulp.task('html-watch', ['html'], function (done) {
    browserSync.reload();
    done();
});

gulp.task('clean', ['clean:js', 'clean:css']);

// js
gulp.task('js_dev', ['vendor:js', 'bundle_dev:js']);

// css
gulp.task('css', ['vendor:css', 'bundle:css']);

gulp.task('serve', function () {
    browserSync.init({
        'port': 8000,
        'server': {
            'baseDir': './dist',
            'middleware': [historyApiFallback()]
        }
    });

    var watcherCSS = gulp.watch(paths.styles.source, ['css-watch']);
    var watcherJS = gulp.watch(paths.js.source, ['js-watch']);
    var watcherHTML = gulp.watch(paths.html.source, ['html-watch']);

    watcherCSS.on('change', function (event) {
        console.log('File ' + event.path + ' was ' + event.type + ', running tasks...');
    });

    watcherJS.on('change', function (event) {
        console.log('File ' + event.path + ' was ' + event.type + ', running tasks...');
    });

    watcherHTML.on('change', function (event) {
        console.log('File ' + event.path + ' was ' + event.type + ', running tasks...');
    });
});

gulp.task('inlinesource', function () {
    return gulp.src('./dist/*.html')
        .pipe(inlinesource())
        .pipe(gulp.dest('./dist'));
});

// Default
gulp.task('default', ['js_dev', 'css', 'html']);

gulp.task('production', function (done) {
    runSequence('clean', 'copy:fonts', 'copy:img', 'default', 'inlinesource', done);
});

// Develop
gulp.task('develop', function (done) {
    runSequence('clean', 'copy:fonts', 'copy:img', 'default', ['serve'], done);
});