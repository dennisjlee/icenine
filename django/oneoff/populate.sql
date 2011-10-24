-- populate icenine2 database from the icenine v1 database

BEGIN;

-- adding this column makes transferring between the two databases much easier
ALTER TABLE icenine2.ice9_directory
ADD COLUMN filedir VARCHAR(255) DEFAULT '';

ALTER TABLE icenine2.ice9_directory
ADD INDEX tempFiledirIndex (filedir);

INSERT INTO icenine2.ice9_directory 
(type, name, parent_id, found, info_link)
VALUES 
('movie', '/', NULL, 1, ''),
('tv', '/', NULL, 1, ''),
('software', '/', NULL, 1, '');

------------------------------------ MOVIES -----------------------------------
-- Movies subdirs level 1
insert into icenine2.ice9_directory
(type, name, parent_id, found, info_link, filedir)
select filetype, filedir, 1, max(found), '', filedir
from icenine.files 
where locate('/', filedir) = 0 and found = 1 and filedir <> ''
and filetype='movie' group by filedir order by filedir;

-- Movie files into ice9_file table, all levels
insert into icenine2.ice9_file
(type, name, path, size, addition_date, found, directory_id, info_link)
select filetype, filename, filepath, filesize, additiondate, f.found, d.id, 
       IFNULL(m.InfoLink, '')
from icenine.files f left join icenine.movies m using (FileID), 
     icenine2.ice9_directory d 
where f.filedir = d.filedir and d.type = f.filetype
and f.filetype = 'movie';

-- Movie files into ice9_movie table, all levels
insert into icenine2.ice9_movie
(file_id, keywords, rating)
select f2.id, m.keywords, m.rating
from icenine.movies m JOIN icenine.files f USING (FileID), icenine2.ice9_file f2
where f.filepath = f2.path and f.filetype = f2.type;


-------------------------------------- TV -------------------------------------

-- TV subdirs level 1
insert into icenine2.ice9_directory
(type, name, parent_id, found, info_link, filedir)
select filetype, filedir, 2, max(found), '', filedir
from icenine.files 
where locate('/', filedir) = 0 and filedir <> ''
and filetype='tv' group by filedir order by filedir;

-- need special cases, these directories have no direct file children
insert into icenine2.ice9_directory
SET type = 'tv', name = 'music_videos', parent_id = 2, found = 1, info_link = '', filedir = 'music_videos';

-- TV subdirs level 2
insert into icenine2.ice9_directory
(type, name, parent_id, found, info_link, filedir)
select f.filetype, 
       substring(substring_index(f.filedir, '/', 2),
                 length(substring_index(f.filedir, '/', 2-1)) + 2) as dir,
       d.id, max(f.found), '', f.filedir
from icenine.files f, icenine2.ice9_directory d
where f.filetype = 'tv'
and substring_index(f.filedir, '/', 2-1) = d.filedir
group by dir having dir <> '' order by f.filedir;

-- special cases
insert into icenine2.ice9_directory
(type, name, parent_id, found, info_link, filedir)
select type, 'downloaded', id, found, '', 'sex_and_the_city/downloaded'
from icenine2.ice9_directory d
where d.filedir = 'sex_and_the_city';

insert into icenine2.ice9_directory
(type, name, parent_id, found, info_link, filedir)
select type, 'extras', id, found, '', 'sex_and_the_city/downloaded/extras'
from icenine2.ice9_directory d
where d.filedir = 'sex_and_the_city/downloaded';

-- TV files all levels
insert into icenine2.ice9_file
(type, name, path, size, addition_date, found, directory_id, info_link)
select filetype, filename, filepath, filesize, additiondate, f.found, d.id, ''
from icenine.files f, icenine2.ice9_directory d
where f.filedir = d.filedir and d.type = f.filetype
and f.filetype = 'tv';

----------------------------------- Software -----------------------------------
-- Software subdirs level 1
insert into icenine2.ice9_directory
(type, name, parent_id, found, info_link, filedir)
select filetype, filedir, 3, max(found), '', filedir
from icenine.files 
where locate('/', filedir) = 0 and filedir <> ''
and filetype='software' group by filedir order by filedir;

-- Software files all levels
insert into icenine2.ice9_file
(type, name, path, size, addition_date, found, directory_id, info_link)
select filetype, filename, filepath, filesize, additiondate, f.found, d.id, ''
from icenine.files f, icenine2.ice9_directory d
where f.filedir = d.filedir and d.type = f.filetype
and f.filetype = 'software';

-- Users
insert into icenine2.ice9_user
(user_id, legacy_id, email, full_name, comment, addition_date)
select -UserID, UserID, Email, FullName, Comment, AdditionDate
from icenine.users;

-- Logs
insert into icenine2.ice9_log
(completed, user_id, file_id, start_time, error_message, ip_address)
select l.Completed, u2.legacy_id, f2.id, l.StartTime, '', l.IPAddress
from icenine.logs l join icenine.files f1 using (FileID)
     join icenine.users u1 on u1.UserID = l.UserID, 
     icenine2.ice9_user u2, icenine2.ice9_file f2
where u1.Email = u2.email and f1.filepath = f2.path;


ALTER TABLE icenine2.ice9_directory
DROP INDEX tempFiledirIndex;

ALTER TABLE icenine2.ice9_directory
DROP COLUMN filedir;

COMMIT;
