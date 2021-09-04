import { Component } from '@angular/core';

@Component({
  selector: 'app-flask-admin',
  template: `
    <iframe src="http://nas.lan:8080/finance/admin"></iframe>
  `,
  styles: [
    'body {margin: 0;}',
    'iframe {display: block;border: none;height: 100vh;width: 100vw;}'
  ]
})
export class FlaskAdminComponent{}
