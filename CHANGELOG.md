# CHANGELOG

## v0.5.0 - 15.09.2020

### Added

* Option view set to make manipulations with options
* Image to poll model
* Description to poll model

### Deleted

* Logic to create poll with options
* Options from poll serializer
* Permission file, because now using build in from `rest_framework`

## v0.4.1 - 27.08.2020

### Changed

* Max length for media field in option model

## v0.4.0 - 26.08.2020

### Added

* Polls logic for read, create and delete
* Upload static content logic

## v0.3.0 - 23.08.2020

### Added

* Forget/Reset password functionality
* Change password functionality

### Changed

* All used `os.environ.get` to `env` from `environs` library

## v0.2.0 - 22.08.2020

### Added

* User profile update and retrieve endpoints

## v0.1.0 - 11.08.2020

### Added

* Initialize project
* Sign Up logic
