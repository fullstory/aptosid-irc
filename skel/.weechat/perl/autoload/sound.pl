#!/usr/bin/perl
## =============================================================================
##  sound.pl (c) February 2005 by FlashCode <flashcode@flashtux.org>
##  Updated on 2005-06-04 by FlashCode <flashcode@flashtux.org>
##  Perl script for WeeChat.
##
##  Play a sound when highlighted/private msg, or for ctcp sound event
##  You have to configure $sound_cmd_highlight and $sound_cmd_ctcp below.
## =============================================================================
my $version = "0.2";
my $sound_cmd_highlight = "esdplay ~/highlight_sound.wav >/dev/null 2>&1 &";
my $sound_cmd_ctcp = "esdplay \$filename >/dev/null 2>&1 &";
weechat::register ("Sound", $version, "", "Sound for highlights/privates & CTCP sound events");

weechat::add_message_handler("PRIVMSG", "sound");
weechat::add_command_handler ("sound", sound_cmd);

sub sound
{
    $server = $_[0];
    if ($_[1] =~ /(.*) PRIVMSG (.*)/)
    {
        my $host = $1;
        my $msg = $2;
        if ($host ne "localhost")
        {
            system($sound_cmd_highlight) if (index($msg, weechat::get_info("nick", $server)) != -1);
            if ($msg =~ /\001SOUND ([^ ]*)\001/)
            {
                my $filename = $1;
                my $command = $sound_cmd_ctcp;
                $command =~ s/(\$\w+)/$1/gee;
                system($command);
            }
        }
    }
    return 0;
}

sub sound_cmd
{
    if ($#_ == 1)
    {
        my $filename = $_[1].".wav";
        my $command = $sound_cmd_ctcp;
        $command =~ s/(\$\w+)/$1/gee;
        system($command);
        weechat::command("PRIVMSG ".weechat::get_info("channel")." :\001SOUND $filename\001") if (@_);
    }
}
