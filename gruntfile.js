module.exports = function(grunt) {

    grunt.loadNpmTasks('grunt-contrib-qunit');
    grunt.loadNpmTasks('grunt-contrib-connect');

    // Detect Chromium executable using 'which' command
    const { execSync } = require('child_process');
    let chromiumPath = null;

    try {
        chromiumPath = execSync('which chromium', { encoding: 'utf8' }).trim();
        grunt.log.writeln(`Found Chromium at: ${chromiumPath}`);
    } catch (e) {
        grunt.log.warn('Chromium not found. Puppeteer will use its bundled Chrome.');
    }

    const puppeteerOptions = chromiumPath ? { executablePath: chromiumPath } : {};

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        connect: {
            server: {
                options: {
                    port: 8000
                }
            }
        },
        qunit: {
            withSandbox: {
                options: {
                    urls: [
                        'http://localhost:8000/afscgapviz/static/test/test.html'
                    ],
                    timeout: 60000,
                    puppeteer: {
                        ...puppeteerOptions,
                        args: []
                    }
                }
            },
            withoutSandbox: {
                options: {
                    urls: [
                        'http://localhost:8000/afscgapviz/static/test/test.html'
                    ],
                    timeout: 60000,
                    puppeteer: {
                        ...puppeteerOptions,
                        args: ['--no-sandbox', '--disable-setuid-sandbox']
                    }
                }
            }
        }
    });

    grunt.registerTask('qunit-with-fallback', function() {
        var done = this.async();

        grunt.log.writeln('Attempting to run Chrome with sandbox enabled...');

        grunt.util.spawn({
            grunt: true,
            args: ['qunit:withSandbox']
        }, function(error, result, code) {
            if (error || code !== 0) {
                grunt.log.warn('Chrome sandbox failed. Falling back to --no-sandbox mode.');
                grunt.log.warn('This may reduce security. Consider running in a proper environment with sandbox support.');

                grunt.task.run('qunit:withoutSandbox');
                done();
            } else {
                grunt.log.ok('Chrome ran successfully with sandbox enabled.');
                done();
            }
        });
    });

    grunt.registerTask('default', ['connect', 'qunit-with-fallback']);

};