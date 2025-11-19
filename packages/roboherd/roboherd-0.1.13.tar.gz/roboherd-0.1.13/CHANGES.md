# Changes to roboherd

## 0.1.13

* add basic setup for bdd
* use optional dependencies for `roboherd[amqp]` and `roboherd[mqtt]`

## 0.1.12

- Add ability to set description by markdown
- Add py.typed [roboherd#54](https://codeberg.org/bovine/roboherd/issues/54)
- Fix typo [roboherd#55](https://codeberg.org/bovine/roboherd/issues/55)

## 0.1.11

- Add `--version` flag [roboherd#50](https://codeberg.org/bovine/roboherd/issues/50)
- Repair passing build_args to docker buildx [roboherd#51](https://codeberg.org/bovine/roboherd/issues/51)

## 0.1.10

- Add check command [roboherd#48](https://codeberg.org/bovine/roboherd/issues/48)

## 0.1.9

- Ensure roboherd terminates on connection close [roboherd#1](https://codeberg.org/bovine/roboherd/issues/1)
- Make doc links clickable [roboherd#44](https://codeberg.org/bovine/roboherd/issues/44)
- Document how to work with cattle_grid in `README.md`

## 0.1.8 ([Milestone](https://codeberg.org/bovine/roboherd/milestone/11129))

- Add ConfigOverrides model [roboherd#43](https://codeberg.org/bovine/roboherd/issues/43)
- Allow to skip startup [roboherd#41](https://codeberg.org/bovine/roboherd/issues/41)

## 0.1.7 ([Milestone](https://codeberg.org/bovine/roboherd/milestone/10741))

- Repair docker file [roboherd#38](https://codeberg.org/bovine/roboherd/issues/38)
- Simplify imports and creating a RoboCow [roboherd#39](https://codeberg.org/bovine/roboherd/issues/39)

## 0.1.6 ([Milestone](https://codeberg.org/bovine/roboherd/milestone/10694))

- Comment on python path [roboherd#34](https://codeberg.org/bovine/roboherd/issues/34)
- Enable direct posting of markdown [roboherd#35](https://codeberg.org/bovine/roboherd/issues/35)

## 0.1.5 ([Milestone](https://codeberg.org/bovine/roboherd/milestone/10581))

- Allow overriding the base_url [roboherd#12](https://codeberg.org/bovine/roboherd/issues/12)
- Separate out the internal state of a RoboCow
- If no preferredUsername is set and handle is updated, send Update Service [roboherd#33](https://codeberg.org/bovine/roboherd/issues/33)
- Add an icon property [roboherd#10](https://codeberg.org/bovine/roboherd/issues/10)
- Added a logo [roboherd#32](https://codeberg.org/bovine/roboherd/issues/32)
- Add PublishActivity annotation [roboherd#30](https://codeberg.org/bovine/roboherd/issues/30)

## 0.1.4 ([Milestone](https://codeberg.org/bovine/roboherd/milestone/10442))

- Type check the project
- No longer require bovine [roboherd#26](https://codeberg.org/bovine/roboherd/issues/26)
- Fixed typo in Dockerfile [roboherd#28](https://codeberg.org/bovine/roboherd/issues/28)

## 0.1.3 ([Milestone](https://codeberg.org/bovine/roboherd/milestone/10441))

- Add information about developement [roboherd#24](https://codeberg.org/bovine/roboherd/issues/24)
- Repair docker build [roboherd#23](https://codeberg.org/bovine/roboherd/issues/23)

## 0.1.1 ([Milestone](https://codeberg.org/bovine/roboherd/milestone/10245))

- Document environment variable overrides [roboherd#16](https://codeberg.org/bovine/roboherd/issues/16)
- Add minimal password length (6 characters) for roboherd register
- Finish documentation [roboherd#6](https://codeberg.org/bovine/roboherd/issues/6)
- Add a roboherd register command
- Repair bovine annotations [roboherd#11](https://codeberg.org/bovine/roboherd/issues/11)
- Enable setting the type of the actor [roboherd#9](https://codeberg.org/bovine/roboherd/issues/9)
- Enable setting PropertyValues for the cow actor [roboherd#4](https://codeberg.org/bovine/roboherd/issues/4)
